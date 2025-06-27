import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Container, Title, Text, Stack, Button, Group, Paper, Loader, Alert, Progress, Table, Badge, ScrollArea, Pagination, Center, Grid, Card } from '@mantine/core';
import { useRouter } from 'next/navigation';
import { IconAlertCircle, IconArrowRight, IconClock, IconCheck, IconX, IconWifi, IconWifiOff } from '@tabler/icons-react';
import { Test, testApi, TestSessionWithTest } from '@/lib/api';
import { MultipleChoiceQuestion, ProblemQuestion } from './index';
import { useAppSelector } from '@/lib/store';
import { useQuery } from '@tanstack/react-query';

interface TestPageProps {
    sessionId: string;
    onConnectionStatusChange?: (status: 'connecting' | 'connected' | 'disconnected') => void;
}

// Constants
const QUESTIONS_PER_PAGE = 10;
const TIMER_INTERVAL = 1000; // 1 second

// Dữ liệu mẫu cho topic tiếp theo (trong thực tế sẽ lấy từ API)
const nextTopics: Record<string, { id: string; title: string }> = {
    'algorithms-basics': { id: 'data-structures', title: 'Cấu trúc dữ liệu' },
    'data-structures': { id: 'sorting-algorithms', title: 'Giải thuật sắp xếp' },
    'sorting-algorithms': { id: 'advanced-algorithms', title: 'Giải thuật nâng cao' }
};

const useTestSessionQuery = (sessionId: string) => {
    return useQuery<TestSessionWithTest, Error>({
        queryKey: ['testSession', sessionId],
        queryFn: async () => {
            const sessionData = await testApi.getTestSession(sessionId);
            if (!sessionData) {
                throw new Error(`Không tìm thấy phiên làm bài với ID: ${sessionId}`);
            }
            return sessionData;
        },
        enabled: !!sessionId,
        refetchInterval: 30000, // Refetch every 30 seconds as fallback
    });
};

export const TestPage: React.FC<TestPageProps> = ({ sessionId, onConnectionStatusChange }) => {
    const router = useRouter();
    const userState = useAppSelector(state => state.user);

    // Pagination states
    const [currentPage, setCurrentPage] = useState(1);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

    // Test states
    const [answers, setAnswers] = useState<Record<string, { selectedOptionId?: string; code?: string; feedback?: { isCorrect: boolean; feedback?: string } }>>(
        {}
    );
    const [submitting, setSubmitting] = useState(false);
    const [testSubmitted, setTestSubmitted] = useState(false);
    const [testResult, setTestResult] = useState<{ score: number; totalQuestions: number; correctAnswers: number } | null>(null);
    const [nextTopic, setNextTopic] = useState<{ id: string; title: string } | null>(null);

    // Review mode
    const [isReviewing, setIsReviewing] = useState(false);

    // Timer and connection states
    const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
    const [isAuthLoading, setIsAuthLoading] = useState(true);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
    const [lastSyncTime, setLastSyncTime] = useState<Date>(new Date());

    // Refs
    const wsRef = useRef<WebSocket | null>(null);
    const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const timerIntervalRef = useRef<NodeJS.Timeout | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const { data: testSession, error, isLoading: loading, refetch } = useTestSessionQuery(sessionId);
    const test = testSession?.test;

    // Calculate pagination
    const totalPages = test ? Math.ceil(test.questions.length / QUESTIONS_PER_PAGE) : 0;
    const startIndex = (currentPage - 1) * QUESTIONS_PER_PAGE;
    const endIndex = Math.min(startIndex + QUESTIONS_PER_PAGE, test?.questions?.length || 0);
    const currentPageQuestions = test?.questions?.slice(startIndex, endIndex) || [];

    // Get current question from current page
    const localQuestionIndex = currentQuestionIndex - startIndex;
    const currentQuestion = currentPageQuestions[localQuestionIndex];

    useEffect(() => {
        // Kiểm tra trạng thái đăng nhập
        if (!userState.isLoading && !userState.isInitial) {
            if (!userState.user) {
                router.push('/auth/login');
            } else {
                setIsAuthLoading(false);
            }
        }
    }, [userState, router]);

    useEffect(() => {
        if (testSession && !isAuthLoading) {
            // Thiết lập next topic nếu có
            if (testSession.test.topicId && nextTopics[testSession.test.topicId.toString()]) {
                setNextTopic(nextTopics[testSession.test.topicId.toString()]);
            }

            // Sử dụng session hiện có từ prop
            setTimeRemaining(testSession.timeRemainingSeconds);
            setCurrentQuestionIndex(testSession.currentQuestionIndex);

            // Calculate current page based on question index
            const page = Math.floor(testSession.currentQuestionIndex / QUESTIONS_PER_PAGE) + 1;
            setCurrentPage(page);

            // Nếu đã có câu trả lời, load lại
            if (testSession.answers && Object.keys(testSession.answers).length > 0) {
                setAnswers(testSession.answers);
            }

            // Kết nối WebSocket
            connectWebSocket(testSession.id);

            // Start timer
            startTimer();
        }

        // Cleanup function
        return () => {
            cleanupConnections();
        };
    }, [testSession, isAuthLoading]);

    // Timer countdown
    const startTimer = useCallback(() => {
        if (timerIntervalRef.current) {
            clearInterval(timerIntervalRef.current);
        }

        timerIntervalRef.current = setInterval(() => {
            setTimeRemaining(prev => {
                if (prev === null || prev <= 0) {
                    // Time's up - auto submit
                    handleTimeUp();
                    return 0;
                }
                return prev - 1;
            });
        }, TIMER_INTERVAL);
    }, []);

    const handleTimeUp = useCallback(async () => {
        if (testSubmitted) return;

        try {
            const result = await testApi.submitTestSession(sessionId, answers);
            setTestResult(result);
            setTestSubmitted(true);
            cleanupConnections();
        } catch (error) {
            console.error('Auto-submit failed:', error);
        }
    }, [sessionId, answers, testSubmitted]);

    // Cleanup connections
    const cleanupConnections = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        if (heartbeatIntervalRef.current) {
            clearInterval(heartbeatIntervalRef.current);
            heartbeatIntervalRef.current = null;
        }
        if (timerIntervalRef.current) {
            clearInterval(timerIntervalRef.current);
            timerIntervalRef.current = null;
        }
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }
    }, []);

    // WebSocket connection with auto-reconnect
    const connectWebSocket = useCallback((sessionId: string) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return wsRef.current;
        }

        cleanupConnections();

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') || window.location.host.replace(':3000', ':8000');
        const wsUrl = `${protocol}//${host}/tests/ws/test-sessions/${sessionId}`;

        console.log('Connecting to WebSocket:', wsUrl);
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket connected');
            setConnectionStatus('connected');
            onConnectionStatusChange?.('connected');
            setLastSyncTime(new Date());

            // Send current state to sync
            ws.send(JSON.stringify({
                type: 'sync',
                currentQuestionIndex,
                answers
            }));

            // Setup heartbeat
            heartbeatIntervalRef.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'ping' }));
                }
            }, 10000);
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                console.log("WebSocket message received:", message);
                setLastSyncTime(new Date());

                switch (message.type) {
                    case "sessionState":
                        if (message.currentQuestionIndex !== undefined) {
                            setCurrentQuestionIndex(message.currentQuestionIndex);
                            const page = Math.floor(message.currentQuestionIndex / QUESTIONS_PER_PAGE) + 1;
                            setCurrentPage(page);
                        }
                        if (message.timeRemainingSeconds !== undefined) {
                            setTimeRemaining(message.timeRemainingSeconds);
                        }
                        if (message.answers) {
                            setAnswers(message.answers);
                        }
                        break;

                    case "timeUpdate":
                        if (message.timeRemainingSeconds !== undefined) {
                            setTimeRemaining(message.timeRemainingSeconds);
                        }
                        break;

                    case "answerSaved":
                        console.log("Answer saved for question:", message.questionId);
                        break;

                    case "questionIndexUpdated":
                        if (message.questionIndex !== undefined) {
                            setCurrentQuestionIndex(message.questionIndex);
                            const page = Math.floor(message.questionIndex / QUESTIONS_PER_PAGE) + 1;
                            setCurrentPage(page);
                        }
                        break;

                    case "pong":
                        // Heartbeat response
                        break;

                    default:
                        console.log("Unknown message type:", message.type);
                }
            } catch (error) {
                console.error("Error parsing WebSocket message:", error);
            }
        };

        ws.onclose = (event) => {
            console.log('WebSocket disconnected', event.code, event.reason);
            setConnectionStatus('disconnected');
            onConnectionStatusChange?.('disconnected');

            // Auto-reconnect after 3 seconds if not intentional close
            if (event.code !== 1000 && event.code !== 1001) {
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connectWebSocket(sessionId);
                }, 3000);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setConnectionStatus('disconnected');
            onConnectionStatusChange?.('disconnected');
        };

        return ws;
    }, [currentQuestionIndex, answers, onConnectionStatusChange]);

    // Sync data when reconnected
    const syncData = useCallback(async () => {
        try {
            const latestSession = await refetch();
            if (latestSession.data) {
                setCurrentQuestionIndex(latestSession.data.currentQuestionIndex);
                setAnswers(latestSession.data.answers);
                setTimeRemaining(latestSession.data.timeRemainingSeconds);

                const page = Math.floor(latestSession.data.currentQuestionIndex / QUESTIONS_PER_PAGE) + 1;
                setCurrentPage(page);
            }
        } catch (error) {
            console.error('Failed to sync data:', error);
        }
    }, [refetch]);

    // Auto-sync data every 30 seconds when disconnected
    useEffect(() => {
        let syncInterval: NodeJS.Timeout;

        if (connectionStatus === 'disconnected') {
            syncInterval = setInterval(syncData, 30000);
        }

        return () => {
            if (syncInterval) {
                clearInterval(syncInterval);
            }
        };
    }, [connectionStatus, syncData]);

    // Update test session
    const updateTestSession = useCallback(async (updates: any) => {
        if (!sessionId) return;

        try {
            const session = await testApi.updateTestSession(sessionId, updates);
            console.log('Test session updated:', session);
        } catch (error) {
            console.error('Failed to update test session:', error);
        }
    }, [sessionId]);

    // Save answer
    const saveAnswer = useCallback(async (questionId: string, answer: any) => {
        if (!sessionId) return;

        try {
            await testApi.submitSessionAnswer(sessionId, questionId, answer);

            // Also send via WebSocket if connected
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({
                    type: 'saveAnswer',
                    questionId,
                    answer
                }));
            }
        } catch (error) {
            console.error('Failed to save answer:', error);
        }
    }, [sessionId]);

    // Navigation functions
    const handleQuestionNavigation = (questionIndex: number) => {
        setCurrentQuestionIndex(questionIndex);
        const page = Math.floor(questionIndex / QUESTIONS_PER_PAGE) + 1;
        setCurrentPage(page);

        updateTestSession({ currentQuestionIndex: questionIndex });

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                type: 'updateQuestionIndex',
                questionIndex
            }));
        }
    };

    const handleNextQuestion = () => {
        if (test && currentQuestionIndex < test.questions.length - 1) {
            handleQuestionNavigation(currentQuestionIndex + 1);
        }
    };

    const handlePreviousQuestion = () => {
        if (currentQuestionIndex > 0) {
            handleQuestionNavigation(currentQuestionIndex - 1);
        }
    };

    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        const newQuestionIndex = (page - 1) * QUESTIONS_PER_PAGE;
        handleQuestionNavigation(newQuestionIndex);
    };

    // Answer submission handlers
    const handleMultipleChoiceSubmit = async (questionId: string, selectedOption: string) => {
        setSubmitting(true);
        try {
            const answer = { selectedOptionId: selectedOption };
            await saveAnswer(questionId, answer);

            setAnswers(prev => ({
                ...prev,
                [questionId]: answer
            }));
        } catch (error) {
            console.error('Failed to submit answer:', error);
        } finally {
            setSubmitting(false);
        }
    };

    const handleProblemSubmit = async (questionId: string, answerText: string) => {
        setSubmitting(true);
        try {
            const answer = { code: answerText };
            await saveAnswer(questionId, answer);

            setAnswers(prev => ({
                ...prev,
                [questionId]: answer
            }));
        } catch (error) {
            console.error('Failed to submit answer:', error);
        } finally {
            setSubmitting(false);
        }
    };

    // Test submission handlers
    const handleSubmitTest = () => {
        setIsReviewing(true);
    };

    const handleFinalSubmit = async () => {
        setSubmitting(true);
        try {
            const result = await testApi.submitTestSession(sessionId, answers);
            setTestResult(result);
            setTestSubmitted(true);
            cleanupConnections();
        } catch (error) {
            console.error('Failed to submit test:', error);
        } finally {
            setSubmitting(false);
            setIsReviewing(false);
        }
    };

    const handleCancelReview = () => {
        setIsReviewing(false);
    };

    const handleGoToNextTopic = () => {
        if (nextTopic) {
            router.push(`/topics/${nextTopic.id}`);
        }
    };

    const handleReturnToTopic = () => {
        if (test?.topicId) {
            router.push(`/topics/${test.topicId}`);
        } else if (test?.courseId) {
            router.push(`/courses/${test.courseId}`);
        } else {
            router.push('/learn');
        }
    };

    // Format time
    const formatTime = (seconds: number): string => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const remainingSeconds = seconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    };

    // Connection status indicator
    const getConnectionIndicator = () => {
        const timeSinceLastSync = new Date().getTime() - lastSyncTime.getTime();
        const isStale = timeSinceLastSync > 60000; // 1 minute

        return (
            <Group gap="xs" align="center">
                {connectionStatus === 'connected' ? (
                    <IconWifi size={16} color="green" />
                ) : (
                    <IconWifiOff size={16} color="red" />
                )}
                <Text size="sm" c={connectionStatus === 'connected' && !isStale ? 'green' : 'red'}>
                    {connectionStatus === 'connected'
                        ? (isStale ? 'Kết nối không ổn định' : 'Đã kết nối')
                        : 'Mất kết nối'
                    }
                </Text>
                {connectionStatus === 'disconnected' && (
                    <Button size="xs" variant="light" onClick={syncData}>
                        Đồng bộ
                    </Button>
                )}
            </Group>
        );
    };

    if (loading || isAuthLoading) {
        return (
            <Container size="md" py="xl">
                <Stack align="center" justify="center" h={400}>
                    <Loader size="lg" />
                    <Text>Đang tải bài kiểm tra...</Text>
                </Stack>
            </Container>
        );
    }

    if (error) {
        return (
            <Container size="md" py="xl">
                <Alert icon={<IconAlertCircle size="1rem" />} title="Lỗi" color="red">
                    {error.message}
                </Alert>
            </Container>
        );
    }

    if (!test) {
        return (
            <Container size="md" py="xl">
                <Alert icon={<IconAlertCircle size="1rem" />} title="Lỗi" color="red">
                    Không tìm thấy bài kiểm tra
                </Alert>
            </Container>
        );
    }

    // Review mode with pagination
    if (isReviewing && test) {
        const answeredQuestions = Object.keys(answers).length;
        const unansweredQuestions = test.questions.length - answeredQuestions;

        return (
            <Container size="lg" py="xl">
                <Paper p="xl" withBorder>
                    <Stack>
                        <Title order={2}>Xem lại bài làm</Title>
                        <Text>Vui lòng kiểm tra lại các câu trả lời của bạn trước khi nộp bài chính thức.</Text>

                        <Alert color="blue" title="Thông tin bài làm">
                            <Text>Số câu đã trả lời: {answeredQuestions}/{test.questions.length}</Text>
                            {unansweredQuestions > 0 && (
                                <Text color="orange">Còn {unansweredQuestions} câu hỏi chưa được trả lời.</Text>
                            )}
                        </Alert>

                        <ScrollArea h={500}>
                            <Grid>
                                {test.questions.map((question, index) => {
                                    const answer = answers[question.id];
                                    const isAnswered = !!answer;

                                    return (
                                        <Grid.Col key={question.id} span={6}>
                                            <Card padding="sm" withBorder>
                                                <Stack gap="xs">
                                                    <Group justify="space-between">
                                                        <Text fw={500}>Câu {index + 1}</Text>
                                                        {isAnswered ? (
                                                            <Badge color="green" size="sm">
                                                                <IconCheck size={12} /> Đã trả lời
                                                            </Badge>
                                                        ) : (
                                                            <Badge color="orange" size="sm">
                                                                <IconX size={12} /> Chưa trả lời
                                                            </Badge>
                                                        )}
                                                    </Group>
                                                    <Text size="sm" lineClamp={2}>
                                                        {question.content}
                                                    </Text>
                                                    <Text size="xs" c="dimmed">
                                                        {question.type === 'single_choice' ? 'Trắc nghiệm' : 'Tự luận'} • {question.difficulty}
                                                    </Text>
                                                    <Button
                                                        size="xs"
                                                        variant="light"
                                                        onClick={() => {
                                                            handleQuestionNavigation(index);
                                                            setIsReviewing(false);
                                                        }}
                                                    >
                                                        {isAnswered ? 'Chỉnh sửa' : 'Trả lời'}
                                                    </Button>
                                                </Stack>
                                            </Card>
                                        </Grid.Col>
                                    );
                                })}
                            </Grid>
                        </ScrollArea>

                        <Group justify="space-between" mt="xl">
                            <Button variant="outline" onClick={handleCancelReview}>
                                Quay lại làm bài
                            </Button>
                            <Button
                                color="green"
                                onClick={handleFinalSubmit}
                                loading={submitting}
                                disabled={submitting}
                            >
                                Nộp bài chính thức
                            </Button>
                        </Group>
                    </Stack>
                </Paper>
            </Container>
        );
    }

    // Test result display
    if (testSubmitted && testResult) {
        const isPassed = testResult.score >= 70;

        return (
            <Container size="md" py="xl">
                <Paper p="xl" withBorder>
                    <Stack align="center">
                        <Title order={2}>Kết quả bài kiểm tra</Title>
                        <Text size="xl" fw={700} color={isPassed ? 'green' : 'red'}>
                            Điểm số: {testResult.score}
                        </Text>
                        <Text>
                            Đúng {testResult.correctAnswers}/{testResult.totalQuestions} câu hỏi
                        </Text>

                        {isPassed ? (
                            <Alert title="Chúc mừng!" color="green" variant="light" w="100%">
                                Bạn đã hoàn thành bài kiểm tra và mở khóa chủ đề tiếp theo trong lộ trình học tập.
                            </Alert>
                        ) : (
                            <Alert title="Chưa đạt yêu cầu" color="yellow" variant="light" w="100%">
                                Bạn cần đạt ít nhất 70% số điểm để mở khóa chủ đề tiếp theo. Hãy ôn tập và thử lại!
                            </Alert>
                        )}

                        <Group mt="lg" justify="center">
                            <Button variant="outline" onClick={handleReturnToTopic}>
                                Quay lại chủ đề
                            </Button>

                            {isPassed && nextTopic && (
                                <Button onClick={handleGoToNextTopic} rightSection={<IconArrowRight size="1rem" />}>
                                    Đến chủ đề {nextTopic.title}
                                </Button>
                            )}
                        </Group>
                    </Stack>
                </Paper>
            </Container>
        );
    }

    // Main test interface
    const progress = test?.questions ? ((Object.keys(answers).length) / test.questions.length) * 100 : 0;
    const currentAnswer = currentQuestion ? answers[currentQuestion.id] : undefined;

    return (
        <Container size="lg" py="md">
            <Stack gap="md">
                {/* Header with timer and connection status */}
                <Paper p="md" withBorder>
                    <Group justify="space-between" align="center">
                        <div>
                            <Title order={2}>Bài Kiểm Tra</Title>
                            <Text c="dimmed" size="sm">
                                Trang {currentPage}/{totalPages} •
                                Câu {currentQuestionIndex + 1}/{test.questions.length}
                            </Text>
                        </div>
                        <Group gap="lg">
                            {getConnectionIndicator()}
                            {timeRemaining !== null && (
                                <Paper p="sm" withBorder>
                                    <Group gap="xs" align="center">
                                        <IconClock
                                            size={16}
                                            color={timeRemaining < 300 ? 'red' : timeRemaining < 900 ? 'orange' : 'blue'}
                                        />
                                        <Text
                                            fw={500}
                                            c={timeRemaining < 300 ? 'red' : timeRemaining < 900 ? 'orange' : undefined}
                                        >
                                            {formatTime(timeRemaining)}
                                        </Text>
                                    </Group>
                                </Paper>
                            )}
                        </Group>
                    </Group>
                </Paper>

                {/* Progress bar */}
                <Paper p="sm" withBorder>
                    <Stack gap="xs">
                        <Group justify="space-between">
                            <Text size="sm" fw={500}>Tiến độ hoàn thành</Text>
                            <Text size="sm" c="dimmed">{Math.round(progress)}%</Text>
                        </Group>
                        <Progress value={progress} color={progress === 100 ? 'green' : 'blue'} />
                    </Stack>
                </Paper>

                {/* Current question */}
                {currentQuestion ? (
                    currentQuestion.type === 'single_choice' ? (
                        <MultipleChoiceQuestion
                            question={currentQuestion}
                            onSubmit={(selectedOption) => handleMultipleChoiceSubmit(currentQuestion.id, selectedOption)}
                            isSubmitting={submitting}
                            feedback={currentAnswer?.feedback}
                            initialAnswer={currentAnswer?.selectedOptionId}
                        />
                    ) : currentQuestion.type === 'essay' ? (
                        <ProblemQuestion
                            question={currentQuestion}
                            onSubmit={(answer) => handleProblemSubmit(currentQuestion.id, answer)}
                            isSubmitting={submitting}
                            feedback={currentAnswer?.feedback}
                            initialAnswer={currentAnswer?.code}
                        />
                    ) : (
                        <Alert color="orange" title="Loại câu hỏi không được hỗ trợ">
                            Loại câu hỏi "{currentQuestion.type}" chưa được hỗ trợ.
                        </Alert>
                    )
                ) : (
                    <Alert color="red" title="Lỗi">
                        Không tìm thấy câu hỏi hiện tại.
                    </Alert>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                    <Paper p="md" withBorder>
                        <Center>
                            <Pagination
                                total={totalPages}
                                value={currentPage}
                                onChange={handlePageChange}
                                size="sm"
                                withEdges
                            />
                        </Center>
                    </Paper>
                )}

                {/* Navigation controls */}
                <Group justify="space-between" mt="lg">
                    <Group>
                        <Button
                            variant="outline"
                            onClick={handlePreviousQuestion}
                            disabled={currentQuestionIndex === 0 || submitting}
                        >
                            Câu trước
                        </Button>
                        {currentQuestionIndex < test.questions.length - 1 && (
                            <Button
                                onClick={handleNextQuestion}
                                disabled={submitting}
                            >
                                Câu tiếp theo
                            </Button>
                        )}
                    </Group>

                    <Group>
                        <Button
                            variant="light"
                            onClick={handleSubmitTest}
                            disabled={submitting}
                        >
                            Xem lại bài làm
                        </Button>

                        <Button
                            color="green"
                            onClick={handleSubmitTest}
                            disabled={submitting}
                            loading={submitting}
                        >
                            Nộp bài
                        </Button>
                    </Group>
                </Group>
            </Stack>
        </Container>
    );
};

export default TestPage; 