import { useState, useEffect, useCallback, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { testApi, TestSessionWithTest, TestAnswer } from '@/lib/api';

type TestState = 'loading' | 'landing' | 'quiz' | 'submitted' | 'error';

export interface UseTestSessionReturn {
    // States
    state: TestState;
    testSession: TestSessionWithTest | null;
    currentQuestionIndex: number;
    timeRemaining: number;
    answers: Record<string, TestAnswer>;
    error: string | null;
    isSubmitting: boolean;

    // Actions
    startTest: () => Promise<void>;
    submitAnswer: (questionId: string, answer: TestAnswer) => Promise<void>;
    submitTest: () => Promise<void>;
    nextQuestion: () => void;
    previousQuestion: () => void;
    goToQuestion: (index: number) => void;

    // Utils
    formatTime: (seconds: number) => string;
    getProgress: () => number;
    canSubmit: () => boolean;
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

    // Refs
    const timerRef = useRef<NodeJS.Timeout | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

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

            // Determine initial state
            if (testSession.status === 'pending') {
                setState('landing');
            } else if (testSession.status === 'in_progress') {
                setState('quiz');
                startTimer();
                connectWebSocket();
            }
        }
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

        try {
            const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/tests/ws/test-sessions/${sessionId}`;
            wsRef.current = new WebSocket(wsUrl);

            wsRef.current.onopen = () => {
                console.log('WebSocket connected');
            };

            wsRef.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.type === 'session_update') {
                        setTimeRemaining(data.timeRemainingSeconds);
                    } else if (data.type === 'auto_submit') {
                        setState('submitted');
                        stopTimer();
                    }
                } catch (error) {
                    console.error('WebSocket message parse error:', error);
                }
            };

            wsRef.current.onclose = () => {
                console.log('WebSocket disconnected');
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('WebSocket connection error:', error);
        }
    }, [sessionId]);

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

    // Submit answer mutation
    const submitAnswerMutation = useMutation({
        mutationFn: ({ questionId, answer }: { questionId: string; answer: TestAnswer }) =>
            testApi.submitSessionAnswer(sessionId, questionId, answer),
        onSuccess: () => {
            // Update session data
            queryClient.invalidateQueries({ queryKey: ['testSession', sessionId] });
        },
        onError: (error: any) => {
            console.error('Submit answer error:', error);
        }
    });

    // Submit test mutation
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

    // Actions
    const startTest = useCallback(async () => {
        if (state !== 'landing') return;
        startTestMutation.mutate();
    }, [state, startTestMutation]);

    const submitAnswer = useCallback(async (questionId: string, answer: TestAnswer) => {
        setAnswers(prev => ({ ...prev, [questionId]: answer }));
        submitAnswerMutation.mutate({ questionId, answer });
    }, [submitAnswerMutation]);

    const submitTest = useCallback(async () => {
        if (isSubmitting) return;
        setIsSubmitting(true);
        submitTestMutation.mutate();
    }, [isSubmitting, submitTestMutation]);

    const nextQuestion = useCallback(() => {
        if (!testSession?.test) return;
        const maxIndex = testSession.test.questions.length - 1;
        setCurrentQuestionIndex(prev => Math.min(prev + 1, maxIndex));
    }, [testSession]);

    const previousQuestion = useCallback(() => {
        setCurrentQuestionIndex(prev => Math.max(prev - 1, 0));
    }, []);

    const goToQuestion = useCallback((index: number) => {
        if (!testSession?.test) return;
        const maxIndex = testSession.test.questions.length - 1;
        setCurrentQuestionIndex(Math.max(0, Math.min(index, maxIndex)));
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
        return (Object.keys(answers).length / testSession.test.questions.length) * 100;
    }, [answers, testSession]);

    const canSubmit = useCallback((): boolean => {
        if (!testSession?.test) return false;
        return Object.keys(answers).length >= testSession.test.questions.length * 0.5; // At least 50% answered
    }, [answers, testSession]);

    // Cleanup
    useEffect(() => {
        return () => {
            stopTimer();
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [stopTimer]);

    return {
        // States
        state,
        testSession,
        currentQuestionIndex,
        timeRemaining,
        answers,
        error,
        isSubmitting,

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