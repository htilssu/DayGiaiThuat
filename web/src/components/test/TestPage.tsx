import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Container, Title, Text, Stack, Button, Group, Paper, Loader, Alert, Progress, Table, Badge, ScrollArea } from '@mantine/core';
import { useRouter } from 'next/navigation';
import { IconAlertCircle, IconArrowRight, IconClock, IconCheck, IconX } from '@tabler/icons-react';
import { Test, testApi, TestSessionWithTest } from '@/lib/api';
import { MultipleChoiceQuestion, ProblemQuestion } from './index';
import { useAppSelector } from '@/lib/store';
import { useQuery } from '@tanstack/react-query';

interface TestPageProps {
    sessionId: string;
    onConnectionStatusChange?: (status: 'connecting' | 'connected' | 'disconnected') => void;
}

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
    });
};

export const TestPage: React.FC<TestPageProps> = ({ sessionId, onConnectionStatusChange }) => {
    const router = useRouter();
    const userState = useAppSelector(state => state.user);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<string, { selectedOptionId?: string; code?: string; feedback?: { isCorrect: boolean; feedback?: string } }>>(
        {}
    );
    const [submitting, setSubmitting] = useState(false);
    const [testSubmitted, setTestSubmitted] = useState(false);
    const [testResult, setTestResult] = useState<{ score: number; totalQuestions: number; correctAnswers: number } | null>(null);
    const [nextTopic, setNextTopic] = useState<{ id: string; title: string } | null>(null);

    // Thêm state cho chế độ xem lại bài làm
    const [isReviewing, setIsReviewing] = useState(false);

    // Thêm state cho test session
    const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
    const [isAuthLoading, setIsAuthLoading] = useState(true);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

    const wsRef = useRef<WebSocket | null>(null);
    const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);

    const { data: testSession, error, isLoading: loading } = useTestSessionQuery(sessionId.toString());
    const test = testSession?.test; // Lấy thông tin bài kiểm tra từ session

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
            if (testSession.test.topicId && nextTopics[testSession.test.topicId]) {
                setNextTopic(nextTopics[testSession.test.topicId]);
            }

            // Sử dụng session hiện có từ prop
            setTimeRemaining(testSession.time_remaining_seconds);
            setCurrentQuestionIndex(testSession.current_question_index);

            // Nếu đã có câu trả lời, load lại
            if (testSession.answers && Object.keys(testSession.answers).length > 0) {
                setAnswers(testSession.answers);
            }

            // Kết nối WebSocket
            connectWebSocket(testSession.id);
        }

        // Cleanup function
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
            if (heartbeatIntervalRef.current) {
                clearInterval(heartbeatIntervalRef.current);
            }
        };
    }, [testSession, isAuthLoading]);


    // WebSocket connection
    const connectWebSocket = useCallback((sessionId: string) => {
        // Xác định WebSocket URL dựa trên môi trường
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

            // Thiết lập heartbeat để giữ kết nối và cập nhật thời gian
            heartbeatIntervalRef.current = setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ type: 'ping' }));
                }
            }, 10000); // 10 giây gửi ping một lần
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                console.log("WebSocket message received:", message);

                switch (message.type) {
                    case "sessionState":
                        // Cập nhật state từ session ban đầu
                        if (message.currentQuestionIndex !== undefined) {
                            setCurrentQuestionIndex(message.currentQuestionIndex);
                        }
                        if (message.timeRemainingSeconds !== undefined) {
                            setTimeRemaining(message.timeRemainingSeconds);
                        }
                        break;

                    case "timeUpdate":
                        // Cập nhật thời gian còn lại
                        if (message.timeRemainingSeconds !== undefined) {
                            setTimeRemaining(message.timeRemainingSeconds);
                        }
                        break;

                    case "answerSaved":
                        // Xác nhận câu trả lời đã được lưu
                        console.log("Answer saved for question:", message.questionId);
                        break;

                    case "questionIndexUpdated":
                        // Cập nhật chỉ số câu hỏi
                        if (message.questionIndex !== undefined) {
                            setCurrentQuestionIndex(message.questionIndex);
                        }
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

            // Tự động reconnect sau 3 giây nếu không phải do lỗi xác thực
            if (event.code !== 1008) {
                setTimeout(() => {
                    if (wsRef.current?.readyState === WebSocket.CLOSED) {
                        connectWebSocket(sessionId);
                    }
                }, 3000);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setConnectionStatus('disconnected');
            onConnectionStatusChange?.('disconnected');
        };

        return ws;
    }, []);

    // Cập nhật tiến trình làm bài
    const updateTestSession = useCallback(async (updates: any) => {
        if (!sessionId) return;

        try {
            await testApi.updateTestSession(sessionId, updates);
        } catch (error) {
            console.error('Error updating test session:', error);
        }
    }, [sessionId]);

    // Auto-save câu trả lời qua WebSocket
    const saveAnswerViaWebSocket = useCallback(
        (questionId: string, answer: any) => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(
                    JSON.stringify({
                        type: "saveAnswer",
                        questionId,
                        answer,
                    })
                );
            }
        },
        []
    );

    // Cập nhật question index qua WebSocket
    const updateQuestionIndexViaWebSocket = useCallback(
        (questionIndex: number) => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(
                    JSON.stringify({
                        type: "updateQuestionIndex",
                        questionIndex,
                    })
                );
            }
        },
        []
    );

    // Xử lý chuyển câu hỏi
    const handleNextQuestion = () => {
        if (!test || currentQuestionIndex >= test.questions.length - 1) return;

        const nextIndex = currentQuestionIndex + 1;
        setCurrentQuestionIndex(nextIndex);

        // Cập nhật qua WebSocket
        updateQuestionIndexViaWebSocket(nextIndex);

        // Fallback qua REST API
        updateTestSession({ current_question_index: nextIndex });
    };

    const handlePreviousQuestion = () => {
        if (currentQuestionIndex <= 0) return;

        const prevIndex = currentQuestionIndex - 1;
        setCurrentQuestionIndex(prevIndex);

        // Cập nhật qua WebSocket  
        updateQuestionIndexViaWebSocket(prevIndex);

        // Fallback qua REST API
        updateTestSession({ current_question_index: prevIndex });
    };

    // Xử lý nộp câu trả lời trắc nghiệm
    const handleMultipleChoiceSubmit = async (questionId: string, selectedOptionId: string) => {
        if (submitting || !sessionId) return;

        // Cập nhật state local ngay lập tức để UX responsive
        const newAnswer = { selectedOptionId };
        setAnswers(prev => ({
            ...prev,
            [questionId]: newAnswer
        }));

        // Auto-save qua WebSocket
        saveAnswerViaWebSocket(questionId, newAnswer);
    };

    // Xử lý nộp câu trả lời lập trình
    const handleProblemSubmit = async (questionId: string, code: string) => {
        if (submitting || !sessionId) return;

        try {
            setSubmitting(true);

            // Lưu câu trả lời vào state
            const updatedAnswers = {
                ...answers,
                [questionId]: { ...answers[questionId], code }
            };
            setAnswers(updatedAnswers);

            await testApi.submitSessionAnswer(parseInt(sessionId), questionId, { code });

        } catch (error) {
            console.error('Error submitting code:', error);
        } finally {
            setSubmitting(false);
        }
    };

    // Xử lý nộp bài
    const handleSubmitTest = () => {
        // Chuyển sang chế độ xem lại bài làm
        setIsReviewing(true);
    };

    // Xử lý nộp bài chính thức
    const handleFinalSubmit = async () => {
        if (submitting || !sessionId) return;

        try {
            setSubmitting(true);

            const result = await testApi.submitTestSession(parseInt(sessionId));

            setTestResult(result);
            setTestSubmitted(true);
            setIsReviewing(false);
        } catch (error) {
            console.error('Error submitting test:', error);
            alert('Có lỗi xảy ra khi nộp bài. Vui lòng thử lại.');
        } finally {
            setSubmitting(false);
        }
    };

    // Hủy xem lại và quay lại làm bài
    const handleCancelReview = () => {
        setIsReviewing(false);
    };

    // Xử lý chuyển đến chủ đề tiếp theo
    const handleGoToNextTopic = () => {
        if (nextTopic) {
            router.push(`/topics/${nextTopic.id}`);
        }
    };

    const handleReturnToTopic = () => {
        if (test?.topicId) {
            router.push(`/topics/${test.topicId}`);
        } else if (isTopicTest) {
            router.push(`/topics/${actualTestId}`);
        } else {
            router.push('/learn');
        }
    };

    // Format thời gian
    const formatTime = (seconds: number): string => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
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

    if (isReviewing && test) {
        // Tính số câu đã trả lời
        const answeredQuestions = Object.keys(answers).length;
        const unansweredQuestions = test.questions.length - answeredQuestions;

        return (
            <Container size="md" py="xl">
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

                        <ScrollArea h={400} type="auto">
                            <Table>
                                <thead>
                                    <tr>
                                        <th>STT</th>
                                        <th>Câu hỏi</th>
                                        <th>Loại</th>
                                        <th>Trạng thái</th>
                                        <th>Hành động</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {test.questions.map((question, index) => {
                                        const answer = answers[question.id];
                                        const isAnswered = !!answer;

                                        return (
                                            <tr key={question.id}>
                                                <td>{index + 1}</td>
                                                <td>
                                                    <Text lineClamp={1}>{question.title}</Text>
                                                </td>
                                                <td>
                                                    {question.type === 'multiple_choice' ? 'Trắc nghiệm' : 'Lập trình'}
                                                </td>
                                                <td>
                                                    {isAnswered ? (
                                                        <Badge color="green" leftSection={<IconCheck size={14} />}>
                                                            Đã trả lời
                                                        </Badge>
                                                    ) : (
                                                        <Badge color="orange" leftSection={<IconX size={14} />}>
                                                            Chưa trả lời
                                                        </Badge>
                                                    )}
                                                </td>
                                                <td>
                                                    <Button
                                                        size="xs"
                                                        variant="light"
                                                        onClick={() => {
                                                            setCurrentQuestionIndex(index);
                                                            setIsReviewing(false);
                                                        }}
                                                    >
                                                        {isAnswered ? 'Chỉnh sửa' : 'Trả lời'}
                                                    </Button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </Table>
                        </ScrollArea>

                        <Group justify="space-between" mt="xl">
                            <Button
                                variant="outline"
                                onClick={handleCancelReview}
                            >
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

    if (testSubmitted && testResult) {
        const isPassed = testResult.score >= 70; // Điểm đạt là 70%

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

    const currentQuestion = test?.questions?.[currentQuestionIndex];
    const currentAnswer = answers[currentQuestion?.id];
    const progress = test?.questions ? ((currentQuestionIndex + 1) / test.questions.length) * 100 : 0;

    return (
        <Container size="md" py="xl">
            <Stack>
                <Group position="apart" align="center">
                    <div>
                        <Title order={2}>{test.title}</Title>
                        <Text color="dimmed">{test.description}</Text>
                    </div>
                    {timeRemaining !== null && (
                        <Paper p="md" withBorder>
                            <Group>
                                <IconClock size="1.2rem" />
                                <Text fw={500}>{formatTime(timeRemaining)}</Text>
                            </Group>
                        </Paper>
                    )}
                </Group>

                <Progress value={progress} size="sm" />

                <Group position="apart">
                    <Text>
                        Câu hỏi {currentQuestionIndex + 1} / {test?.questions?.length || 0}
                    </Text>
                    <Text color={connectionStatus === 'connected' ? 'green' : 'red'}>
                        {connectionStatus === 'connected' ? 'Đã kết nối' : 'Mất kết nối'}
                    </Text>
                </Group>

                {currentQuestion ? (
                    currentQuestion.type === 'multiple_choice' ? (
                        <MultipleChoiceQuestion
                            question={currentQuestion}
                            onSubmit={(selectedOptionId) => handleMultipleChoiceSubmit(currentQuestion.id, selectedOptionId)}
                            isSubmitting={submitting}
                            feedback={currentAnswer?.feedback}
                        />
                    ) : (
                        <ProblemQuestion
                            question={currentQuestion}
                            onSubmit={(code) => handleProblemSubmit(currentQuestion.id, code)}
                            isSubmitting={submitting}
                            feedback={currentAnswer?.feedback}
                        />
                    )
                ) : (
                    <Alert color="red" title="Lỗi">
                        Không tìm thấy câu hỏi hiện tại.
                    </Alert>
                )}

                <Group position="apart" mt="xl">
                    <Button
                        variant="outline"
                        onClick={handlePreviousQuestion}
                        disabled={currentQuestionIndex === 0 || submitting}
                    >
                        Câu trước
                    </Button>

                    <Group>
                        <Button
                            variant="light"
                            onClick={handleSubmitTest}
                            disabled={submitting}
                        >
                            Xem lại bài làm
                        </Button>

                        {currentQuestionIndex < test.questions.length - 1 ? (
                            <Button
                                onClick={handleNextQuestion}
                                disabled={submitting}
                            >
                                Câu tiếp theo
                            </Button>
                        ) : (
                            <Button
                                color="green"
                                onClick={handleSubmitTest}
                                disabled={submitting}
                                loading={submitting}
                            >
                                Nộp bài
                            </Button>
                        )}
                    </Group>
                </Group>
            </Stack>
        </Container>
    );
};

export default TestPage; 