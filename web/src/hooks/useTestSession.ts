import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { testApi, TestSessionWithTest, TestAnswer } from '@/lib/api';

type TestState = 'loading' | 'quiz' | 'submitted' | 'error';

export interface UseTestSessionReturn {
    // States
    state: TestState;
    testSession: TestSessionWithTest | undefined;
    currentQuestionIndex: number;
    timeRemaining: number;
    answers: Record<string, TestAnswer>;
    error: string | null;
    isSubmitting: boolean;

    // Actions
    startTest: () => Promise<void>;
    submitAnswer: (questionId: string, answer: TestAnswer, options?: { immediate?: boolean }) => void;
    submitTest: () => Promise<void>;
    nextQuestion: () => void;
    previousQuestion: () => void;
    goToQuestion: (index: number) => void;

    // Utils
    formatTime: (seconds: number) => string;
    getProgress: () => number;
    canSubmit: () => boolean;

    // WebSocket connection status
    connectionStatus: 'connecting' | 'connected' | 'disconnected';
}

export function useTestSession(sessionId: string): UseTestSessionReturn {
    const queryClient = useQueryClient();

    // States
    const [state, setState] = useState<TestState>('loading');
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [timeRemaining, setTimeRemaining] = useState(0);
    const [answers, setAnswers] = useState<Record<string, TestAnswer>>({});
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');

    // Refs
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
    const debounceTimeouts = useRef<Record<string, NodeJS.Timeout>>({});

    // Fetch test session
    const {
        data: testSession,
        isLoading: sessionLoading,
        error: sessionError,
        refetch
    } = useQuery({
        queryKey: ['testSession', sessionId],
        queryFn: () => testApi.getTestSession(sessionId),
        enabled: !!sessionId,
        retry: 2,
        refetchOnWindowFocus: false,
    });

    // Initialize session data
    useEffect(() => {
        if (sessionLoading) {
            setState('loading');
            return;
        }

        if (sessionError) {
            setState('error');
            setError('Không thể tải thông tin bài kiểm tra');
            return;
        }

        if (testSession) {
            // Check session status
            if (testSession.status === 'completed' || testSession.status === 'expired') {
                setState('submitted');
                return;
            }

            // Initialize session data
            setTimeRemaining(testSession.timeRemainingSeconds);
            setCurrentQuestionIndex(testSession.currentQuestionIndex);
            setAnswers(testSession.answers || {});

        }
        setState('quiz');
        startTimer();
        connectWebSocket();
    }, [testSession, sessionLoading, sessionError]);

    // Timer
    const startTimer = useCallback(() => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
        }

        timerRef.current = setInterval(() => {
            setTimeRemaining(prev => {
                if (prev <= 1) {
                    // Time's up - auto submit
                    submitTest();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
    }, []);

    const stopTimer = useCallback(() => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
            timerRef.current = null;
        }
    }, []);

    // WebSocket connection
    const connectWebSocket = useCallback(() => {
        if (!sessionId) return;

        // Cleanup existing connection
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.close();
        }

        setConnectionStatus('connecting');

        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') ||
                window.location.host.replace(':3000', ':8000');
            const wsUrl = `${protocol}//${host}/tests/ws/test-sessions/${sessionId}`;

            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                setConnectionStatus('connected');

                // Send sync message
                if (wsRef.current) {
                    wsRef.current.send(JSON.stringify({
                        type: 'sync',
                        currentQuestionIndex,
                        answers
                    }));
                }
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    switch (data.type) {
                        case 'pong':
                            // Heartbeat response
                            break;

                        case 'answer_saved':
                            break;

                        case 'session_update':
                            if (data.timeRemainingSeconds !== undefined) {
                                setTimeRemaining(data.timeRemainingSeconds);
                            }
                            break;

                        case 'auto_submit':
                            setState('submitted');
                            stopTimer();
                            break;

                        case 'error':
                            console.error('WebSocket error:', data.message);
                            break;

                        default:
                            console.log('Unknown message type:', data.type);
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            wsRef.current.onclose = (event) => {
                setConnectionStatus('disconnected');

                // Auto-reconnect after 3 seconds if not intentional close
                if (event.code !== 1000 && event.code !== 1001) {
                    reconnectTimeoutRef.current = setTimeout(() => {
                        connectWebSocket();
                    }, 3000);
                }
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
                setConnectionStatus('disconnected');
            };

        } catch (error) {
            console.error('WebSocket connection error:', error);
            setConnectionStatus('disconnected');
        }
    }, [sessionId, currentQuestionIndex, answers]);

    // Send answer via WebSocket
    const sendAnswerViaSocket = useCallback((questionId: string, answer: TestAnswer) => {
        if (!sessionId) return;

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'save_answer',
                question_id: questionId,
                answer
            }));
        } else {
            console.warn('⚠️ WebSocket not connected, cannot save answer');
        }
    }, [sessionId]);

    // Get question type for debounce logic
    const getQuestionType = useCallback((questionId: string): 'single_choice' | 'essay' | null => {
        if (!testSession?.test) return null;
        const question = testSession.test.questions.find(q => q.id === questionId);
        return question?.type || null;
    }, [testSession]);

    // Start test mutation
    const startTestMutation = useMutation({
        mutationFn: () => testApi.startTestSession(sessionId),
        onSuccess: () => {
            setState('quiz');
            startTimer();
            connectWebSocket();
            queryClient.invalidateQueries({ queryKey: ['testSession', sessionId] });
        },
        onError: (error: any) => {
            setError('Không thể bắt đầu bài kiểm tra');
            console.error('Start test error:', error);
        }
    });

    // Submit test mutation (vẫn dùng HTTP cho final submission)
    const submitTestMutation = useMutation({
        mutationFn: () => testApi.submitTestSession(sessionId, answers),
        onSuccess: () => {
            setState('submitted');
            stopTimer();
            if (wsRef.current) {
                wsRef.current.close();
            }
            queryClient.invalidateQueries({ queryKey: ['testSession', sessionId] });
        },
        onError: (error: any) => {
            setError('Không thể nộp bài kiểm tra');
            console.error('Submit test error:', error);
            setIsSubmitting(false);
        }
    });

    // Cleanup
    useEffect(() => {
        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
            // Cleanup debounce timeouts
            Object.values(debounceTimeouts.current).forEach(timeout => {
                clearTimeout(timeout);
            });
        };
    }, []);

    // Actions
    const startTest = useCallback(async () => {
        startTestMutation.mutate();
    }, [startTestMutation]);

    const submitAnswer = useCallback((questionId: string, answer: TestAnswer, options?: { immediate?: boolean }) => {
        // Cập nhật state local ngay lập tức
        setAnswers(prev => ({ ...prev, [questionId]: answer }));

        const questionType = getQuestionType(questionId);
        const immediate = options?.immediate || false;

        // Clear existing debounce timeout for this question
        if (debounceTimeouts.current[questionId]) {
            clearTimeout(debounceTimeouts.current[questionId]);
            delete debounceTimeouts.current[questionId];
        }

        if (immediate || questionType === 'single_choice') {
            // Send immediately for multiple choice or when explicitly requested
            sendAnswerViaSocket(questionId, answer);
        } else if (questionType === 'essay') {
            // Debounce for essay questions (1.5 seconds)
            debounceTimeouts.current[questionId] = setTimeout(() => {
                sendAnswerViaSocket(questionId, answer);
                delete debounceTimeouts.current[questionId];
            }, 1500);
        } else {
            // Fallback - send immediately if question type unknown
            sendAnswerViaSocket(questionId, answer);
        }
    }, [sendAnswerViaSocket, getQuestionType]);

    const submitTest = useCallback(async () => {
        if (isSubmitting) return;
        setIsSubmitting(true);

        // Clear all pending debounce timeouts and send immediately
        Object.entries(debounceTimeouts.current).forEach(([questionId, timeout]) => {
            clearTimeout(timeout);
            const currentAnswer = answers[questionId];
            if (currentAnswer) {
                sendAnswerViaSocket(questionId, currentAnswer);
            }
        });
        debounceTimeouts.current = {};

        // Wait a bit for final answers to be sent
        setTimeout(() => {
            submitTestMutation.mutate();
        }, 500);
    }, [isSubmitting, submitTestMutation, answers, sendAnswerViaSocket]);

    const nextQuestion = useCallback(() => {
        if (!testSession?.test) return;
        const maxIndex = testSession.test.questions.length - 1;
        const newIndex = Math.min(currentQuestionIndex + 1, maxIndex);
        setCurrentQuestionIndex(newIndex);

        // Sync với server
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'updateQuestionIndex',
                questionIndex: newIndex
            }));
        }
    }, [testSession, currentQuestionIndex]);

    const previousQuestion = useCallback(() => {
        const newIndex = Math.max(currentQuestionIndex - 1, 0);
        setCurrentQuestionIndex(newIndex);

        // Sync với server
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'updateQuestionIndex',
                questionIndex: newIndex
            }));
        }
    }, [currentQuestionIndex]);

    const goToQuestion = useCallback((index: number) => {
        if (!testSession?.test) return;
        const maxIndex = testSession.test.questions.length - 1;
        const newIndex = Math.max(0, Math.min(index, maxIndex));
        setCurrentQuestionIndex(newIndex);

        // Sync với server
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'updateQuestionIndex',
                questionIndex: newIndex
            }));
        }
    }, [testSession]);

    // Utils
    const formatTime = useCallback((seconds: number): string => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }, []);

    const getProgress = useCallback((): number => {
        if (!testSession?.test) return 0;
        const answeredQuestions = Object.keys(answers).length;
        return (answeredQuestions / testSession.test.questions.length) * 100;
    }, [testSession, answers]);

    const canSubmit = useCallback((): boolean => {
        if (!testSession?.test) return false;
        return Object.keys(answers).length > 0;
    }, [testSession, answers]);

    return {
        // States
        state,
        testSession,
        currentQuestionIndex,
        timeRemaining,
        answers,
        error,
        isSubmitting,
        connectionStatus,

        // Actions
        startTest,
        submitAnswer,
        submitTest,
        nextQuestion,
        previousQuestion,
        goToQuestion,

        // Utils
        formatTime,
        getProgress,
        canSubmit,
    };
} 