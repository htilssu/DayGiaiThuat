'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
    Container,
    Title,
    Text,
    Paper,
    Loader,
    Alert,
    Stack,
    Progress,
    Badge,
    Group,
    ActionIcon,
    Divider
} from '@mantine/core';
import {
    IconWifi,
    IconWifiOff,
    IconClock,
    IconCheck,
    IconX,
    IconAlertTriangle
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { testApi } from '@/lib/api';
import { TestPage } from '@/components/test';
import { useAppSelector } from '@/lib/store';

const ClientPage: React.FC = () => {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.id as string;
    const userState = useAppSelector((state) => state.user);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

    // Debug logging
    useEffect(() => {
        console.log('🧪 TestSession Debug:', {
            sessionId,
            userState: {
                isLoading: userState.isLoading,
                isInitial: userState.isInitial,
                hasUser: !!userState.user,
                userId: userState.user?.id
            }
        });
    }, [sessionId, userState]);

    // Fetch test session data
    const {
        data: testSession,
        isLoading,
        error,
        refetch
    } = useQuery({
        queryKey: ['testSession', sessionId],
        queryFn: async () => {
            console.log('🔄 Fetching test session:', sessionId);
            try {
                const result = await testApi.getTestSession(sessionId);
                console.log('✅ Test session fetched successfully:', result);
                return result;
            } catch (err) {
                console.error('❌ Error fetching test session:', err);
                throw err;
            }
        },
        enabled: !!sessionId && !!userState.user,
        retry: 2,
        refetchOnWindowFocus: false,
    });

    // Debug logging for query state
    useEffect(() => {
        console.log('📊 Query State:', {
            isLoading,
            error: error ? {
                message: (error as any)?.message,
                response: (error as any)?.response?.data,
                status: (error as any)?.response?.status
            } : null,
            hasData: !!testSession,
            testSession: testSession ? {
                id: testSession.id,
                status: testSession.status,
                hasTest: !!testSession.test,
                questionsCount: testSession.test?.questions?.length
            } : null
        });
    }, [isLoading, error, testSession]);

    // Redirect if not authenticated
    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
            console.log('🔒 User not authenticated, redirecting to login');
            router.push('/auth/login');
        }
    }, [userState, router]);

    // Calculate progress
    const calculateProgress = () => {
        if (!testSession?.test?.questions || !testSession.answers) return 0;
        const totalQuestions = testSession.test.questions.length;
        const answeredQuestions = Object.keys(testSession.answers).length;
        return totalQuestions > 0 ? (answeredQuestions / totalQuestions) * 100 : 0;
    };

    // Format time remaining
    const formatTimeRemaining = (seconds: number) => {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    };

    // Connection status badge
    const getConnectionBadge = () => {
        switch (connectionStatus) {
            case 'connected':
                return (
                    <Badge color="green" leftSection={<IconWifi size={12} />}>
                        Đã kết nối
                    </Badge>
                );
            case 'connecting':
                return (
                    <Badge color="yellow" leftSection={<Loader size={12} />}>
                        Đang kết nối...
                    </Badge>
                );
            case 'disconnected':
                return (
                    <Badge color="red" leftSection={<IconWifiOff size={12} />}>
                        Mất kết nối
                    </Badge>
                );
        }
    };

    // Status badge
    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'in_progress':
                return <Badge color="blue">Đang làm bài</Badge>;
            case 'completed':
                return <Badge color="green">Đã hoàn thành</Badge>;
            case 'expired':
                return <Badge color="red">Hết thời gian</Badge>;
            default:
                return <Badge color="gray">{status}</Badge>;
        }
    };

    if (isLoading) {
        return (
            <Container size="md" py="xl">
                <Paper p="xl" shadow="sm" withBorder>
                    <Stack align="center" gap="md">
                        <Loader size="lg" />
                        <Text>Đang tải bài kiểm tra...</Text>
                    </Stack>
                </Paper>
            </Container>
        );
    }

    if (error) {
        return (
            <Container size="md" py="xl">
                <Alert color="red" title="Lỗi" icon={<IconX size={16} />}>
                    <Text mb="md">
                        {(error as any)?.response?.data?.detail || 'Không thể tải bài kiểm tra. Vui lòng thử lại.'}
                    </Text>
                    <Group gap="xs">
                        <ActionIcon variant="light" color="blue" onClick={() => refetch()}>
                            Thử lại
                        </ActionIcon>
                        <ActionIcon variant="light" color="gray" onClick={() => router.back()}>
                            Quay lại
                        </ActionIcon>
                    </Group>
                </Alert>
            </Container>
        );
    }

    if (!testSession) {
        return (
            <Container size="md" py="xl">
                <Alert color="orange" title="Không tìm thấy" icon={<IconAlertTriangle size={16} />}>
                    <Text>Không tìm thấy phiên làm bài này.</Text>
                </Alert>
            </Container>
        );
    }

    const progress = calculateProgress();

    return (
        <Container size="xl" py="md">
            {/* Header với thông tin session */}
            <Paper p="md" shadow="sm" withBorder mb="md">
                <Group justify="space-between" align="center">
                    <Stack gap={4}>
                        <Group gap="md" align="center">
                            <Title order={3}>Bài Kiểm Tra</Title>
                            {getConnectionBadge()}
                            {getStatusBadge(testSession.status)}
                        </Group>
                        {testSession.test && (
                            <Text c="dimmed" size="sm">
                                Câu hỏi: {testSession.test.questions.length} •
                                Thời gian: {testSession.test.durationMinutes} phút •
                                Câu hiện tại: {testSession.currentQuestionIndex + 1}/{testSession.test.questions.length}
                            </Text>
                        )}
                    </Stack>

                    <Stack gap={4} align="end">
                        <Group gap="xs" align="center">
                            <IconClock size={16} />
                            <Text fw={500} c={testSession.timeRemainingSeconds < 300 ? 'red' : undefined}>
                                {formatTimeRemaining(testSession.timeRemainingSeconds)}
                            </Text>
                        </Group>
                        <Text c="dimmed" size="sm">
                            {testSession.isSubmitted ? 'Đã nộp bài' : 'Chưa nộp bài'}
                        </Text>
                    </Stack>
                </Group>

                <Divider my="sm" />

                {/* Progress bar */}
                <Stack gap="xs">
                    <Group justify="space-between" align="center">
                        <Text size="sm" fw={500}>Tiến độ hoàn thành</Text>
                        <Text size="sm" c="dimmed">{Math.round(progress)}%</Text>
                    </Group>
                    <Progress value={progress} color={progress === 100 ? 'green' : 'blue'} />
                </Stack>

                {/* Test results (if completed) */}
                {testSession.isSubmitted && testSession.score !== null && (
                    <>
                        <Divider my="sm" />
                        <Group justify="space-between" align="center">
                            <Text size="sm" fw={500}>Kết quả:</Text>
                            <Group gap="md">
                                <Text size="sm">
                                    Điểm: <span style={{ fontWeight: 500 }}>{testSession.score}/100</span>
                                </Text>
                                {testSession.correctAnswers !== null && (
                                    <Text size="sm">
                                        Đúng: <span style={{ fontWeight: 500 }}>{testSession.correctAnswers}/{testSession.test.questions.length}</span>
                                    </Text>
                                )}
                            </Group>
                        </Group>
                    </>
                )}
            </Paper>

            {/* Test content */}
            <TestPage
                sessionId={sessionId}
                onConnectionStatusChange={setConnectionStatus}
            />
        </Container>
    );
};

export default ClientPage; 