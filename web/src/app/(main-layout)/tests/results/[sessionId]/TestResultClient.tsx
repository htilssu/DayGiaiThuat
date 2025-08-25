'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
    Container,
    Paper,
    Title,
    Text,
    Button,
    Group,
    Stack,
    Alert,
    Loader,
    Progress,
    Badge,
    Card,
    SimpleGrid,
    ThemeIcon,
    Divider,
    ActionIcon,
    Tooltip
} from '@mantine/core';
import {
    IconTrophy,
    IconAlertCircle,
    IconCheck,
    IconX,
    IconClock,
    IconTarget,
    IconBookmark,
    IconHome,
    IconRefresh,
    IconShare,
    IconDownload,
    IconChartBar
} from '@tabler/icons-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useAppSelector } from '@/lib/store';
import { testApi, coursesApi } from '@/lib/api';
import { notifications } from '@mantine/notifications';

interface TestResultClientProps {
    sessionId: string;
}

const TestResultClient: React.FC<TestResultClientProps> = ({ sessionId }) => {
    const router = useRouter();
    const userState = useAppSelector(state => state.user);

    // Redirect if not authenticated
    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
            router.push('/auth/login');
        }
    }, [userState, router]);

    // Fetch test result
    const { data: testResult, isLoading: resultLoading, error: resultError } = useQuery({
        queryKey: ['testResult', sessionId],
        queryFn: () => testApi.getTestResult(sessionId),
        enabled: !!userState.user && !!sessionId,
        retry: false,
    });

    // Fetch test session details
    const { data: testSession, isLoading: sessionLoading } = useQuery({
        queryKey: ['testSession', sessionId],
        queryFn: () => testApi.getTestSession(sessionId),
        enabled: !!userState.user && !!sessionId,
        retry: false,
    });

    // Auto-mark course completion if test is passed
    const markCourseCompletionMutation = useMutation({
        mutationFn: ({ courseId, sessionId }: { courseId: number; sessionId: string }) =>
            coursesApi.markCourseCompleted(courseId, sessionId),
        onSuccess: () => {
            notifications.show({
                title: 'Khóa học hoàn thành!',
                message: 'Chúc mừng bạn đã hoàn thành khóa học thành công!',
                color: 'green',
            });
        },
        onError: (error: any) => {
            console.error('Error marking course completion:', error);
            // Don't show error notification as this is not critical
        },
    });

    // Check if course should be marked as completed
    useEffect(() => {
        if (testResult && testSession && userState.user) {
            const scorePercentage = (testResult.score / testResult.totalQuestions) * 100;
            const isPassed = testSession?.test?.passingScore ? scorePercentage >= testSession.test.passingScore : scorePercentage >= 70;
            
            if (isPassed && testSession.test?.courseId) {
                // Mark course as completed
                markCourseCompletionMutation.mutate({
                    courseId: testSession.test.courseId,
                    sessionId: sessionId
                });
            }
        }
    }, [testResult, testSession, userState.user, sessionId]);

    // Show loading during auth check
    if (userState.isLoading || userState.isInitial) {
        return (
            <Container size="md" py="xl">
                <Stack align="center" gap="md">
                    <Loader size="lg" />
                    <Text>Đang kiểm tra thông tin đăng nhập...</Text>
                </Stack>
            </Container>
        );
    }

    // If not authenticated, will be redirected by useEffect
    if (!userState.user) {
        return null;
    }

    // Loading state
    const isLoading = resultLoading || sessionLoading;
    if (isLoading) {
        return (
            <Container size="md" py="xl">
                <Stack align="center" gap="md">
                    <Loader size="lg" />
                    <Text>Đang tải kết quả bài kiểm tra...</Text>
                </Stack>
            </Container>
        );
    }

    // Error state
    if (resultError || !testResult) {
        return (
            <Container size="md" py="xl">
                <Alert
                    icon={<IconAlertCircle size="1rem" />}
                    title="Lỗi tải kết quả"
                    color="red"
                    mb="lg"
                >
                    {resultError?.message || 'Không thể tải kết quả bài kiểm tra. Vui lòng thử lại sau.'}
                </Alert>
                <Group>
                    <Button onClick={() => window.location.reload()} leftSection={<IconRefresh size="1rem" />}>
                        Thử lại
                    </Button>
                    <Button variant="outline" onClick={() => router.push('/tests')}>
                        Quay về danh sách kiểm tra
                    </Button>
                </Group>
            </Container>
        );
    }

    const scorePercentage = (testResult.score / testResult.totalQuestions) * 100;
    const isPassed = testSession?.test?.passingScore ? scorePercentage >= testSession.test.passingScore : scorePercentage >= 70;

    const getScoreColor = () => {
        if (scorePercentage >= 90) return 'green';
        if (scorePercentage >= 70) return 'blue';
        if (scorePercentage >= 50) return 'yellow';
        return 'red';
    };

    const handleShare = () => {
        if (navigator.share) {
            navigator.share({
                title: 'Kết quả bài kiểm tra',
                text: `Tôi vừa hoàn thành bài kiểm tra với điểm số ${testResult.correctAnswers}/${testResult.totalQuestions}!`,
                url: window.location.href,
            });
        } else {
            navigator.clipboard.writeText(window.location.href);
            notifications.show({
                title: 'Đã sao chép',
                message: 'Đường link đã được sao chép vào clipboard',
                color: 'green',
            });
        }
    };

    return (
        <Container size="md" py="xl">
            <Stack gap="xl">
                {/* Header */}
                <Paper p="xl" radius="md" withBorder>
                    <Stack align="center" gap="lg">
                        <ThemeIcon
                            size={80}
                            radius="xl"
                            color={isPassed ? 'green' : 'red'}
                            variant="light"
                        >
                            {isPassed ? <IconTrophy size="2.5rem" /> : <IconX size="2.5rem" />}
                        </ThemeIcon>
                        
                        <Stack align="center" gap="xs">
                            <Title order={1} ta="center">
                                {isPassed ? 'Chúc mừng! Bạn đã vượt qua bài kiểm tra' : 'Chưa đạt yêu cầu'}
                            </Title>
                            <Text size="lg" c="dimmed" ta="center">
                                {testSession?.test ? `Bài kiểm tra: ${testSession.test.id}` : 'Kết quả bài kiểm tra'}
                            </Text>
                        </Stack>

                        <Badge
                            size="xl"
                            color={getScoreColor()}
                            variant="light"
                            radius="md"
                        >
                            {testResult.correctAnswers}/{testResult.totalQuestions} câu đúng ({scorePercentage.toFixed(1)}%)
                        </Badge>
                    </Stack>
                </Paper>

                {/* Detailed Stats */}
                <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="md">
                    <Card padding="lg" radius="md" withBorder>
                        <Group gap="sm">
                            <ThemeIcon size="lg" color="blue" variant="light">
                                <IconTarget size="1.5rem" />
                            </ThemeIcon>
                            <div>
                                <Text fw={500}>Điểm số</Text>
                                <Text size="xl" fw={700} c={getScoreColor()}>
                                    {scorePercentage.toFixed(1)}%
                                </Text>
                            </div>
                        </Group>
                    </Card>

                    <Card padding="lg" radius="md" withBorder>
                        <Group gap="sm">
                            <ThemeIcon size="lg" color="green" variant="light">
                                <IconCheck size="1.5rem" />
                            </ThemeIcon>
                            <div>
                                <Text fw={500}>Câu đúng</Text>
                                <Text size="xl" fw={700} c="green">
                                    {testResult.correctAnswers}
                                </Text>
                            </div>
                        </Group>
                    </Card>

                    <Card padding="lg" radius="md" withBorder>
                        <Group gap="sm">
                            <ThemeIcon size="lg" color="gray" variant="light">
                                <IconChartBar size="1.5rem" />
                            </ThemeIcon>
                            <div>
                                <Text fw={500}>Tổng câu hỏi</Text>
                                <Text size="xl" fw={700}>
                                    {testResult.totalQuestions}
                                </Text>
                            </div>
                        </Group>
                    </Card>
                </SimpleGrid>

                {/* Progress Bar */}
                <Paper p="lg" radius="md" withBorder>
                    <Stack gap="sm">
                        <Group justify="space-between">
                            <Text fw={500}>Tiến độ hoàn thành</Text>
                            <Text fw={500} c={getScoreColor()}>
                                {scorePercentage.toFixed(1)}%
                            </Text>
                        </Group>
                        <Progress
                            value={scorePercentage}
                            color={getScoreColor()}
                            size="lg"
                            radius="md"
                        />
                        {testSession?.test?.passingScore && (
                            <Text size="sm" c="dimmed">
                                Điểm chuẩn để đạt: {testSession.test.passingScore}%
                            </Text>
                        )}
                    </Stack>
                </Paper>

                {/* Course Progress Integration */}
                {testSession?.test?.courseId && isPassed && (
                    <Alert
                        icon={<IconBookmark size="1rem" />}
                        title="Tiến độ khóa học được cập nhật"
                        color="green"
                    >
                        Bạn đã hoàn thành bài kiểm tra này! Tiến độ khóa học của bạn đã được cập nhật.
                    </Alert>
                )}

                {/* Action Buttons */}
                <Paper p="lg" radius="md" withBorder>
                    <Stack gap="md">
                        <Text fw={500} size="lg">Bước tiếp theo</Text>
                        <Group grow>
                            {testSession?.test?.courseId && (
                                <Button
                                    leftSection={<IconBookmark size="1rem" />}
                                    onClick={() => router.push(`/courses/${testSession.test.courseId}`)}
                                >
                                    Tiếp tục khóa học
                                </Button>
                            )}
                            <Button
                                variant="outline"
                                leftSection={<IconHome size="1rem" />}
                                onClick={() => router.push('/tests')}
                            >
                                Danh sách kiểm tra
                            </Button>
                        </Group>
                        
                        <Divider />
                        
                        <Group justify="center">
                            <Tooltip label="Chia sẻ kết quả">
                                <ActionIcon variant="light" size="lg" onClick={handleShare}>
                                    <IconShare size="1.2rem" />
                                </ActionIcon>
                            </Tooltip>
                            <Tooltip label="Tải xuống kết quả">
                                <ActionIcon variant="light" size="lg" onClick={() => window.print()}>
                                    <IconDownload size="1.2rem" />
                                </ActionIcon>
                            </Tooltip>
                        </Group>
                    </Stack>
                </Paper>

                {/* Detailed Feedback */}
                {testResult.feedback && Object.keys(testResult.feedback).length > 0 && (
                    <Paper p="lg" radius="md" withBorder>
                        <Stack gap="md">
                            <Text fw={500} size="lg">Chi tiết kết quả</Text>
                            {Object.entries(testResult.feedback).map(([questionId, feedback]) => (
                                <Group key={questionId} justify="space-between" wrap="nowrap">
                                    <Text size="sm">Câu {questionId}</Text>
                                    <Group gap="xs">
                                        <ThemeIcon
                                            size="sm"
                                            color={feedback.isCorrect ? 'green' : 'red'}
                                            variant="light"
                                        >
                                            {feedback.isCorrect ? <IconCheck size="0.8rem" /> : <IconX size="0.8rem" />}
                                        </ThemeIcon>
                                        {feedback.feedback && (
                                            <Text size="xs" c="dimmed">
                                                {feedback.feedback}
                                            </Text>
                                        )}
                                    </Group>
                                </Group>
                            ))}
                        </Stack>
                    </Paper>
                )}
            </Stack>
        </Container>
    );
};

export default TestResultClient;