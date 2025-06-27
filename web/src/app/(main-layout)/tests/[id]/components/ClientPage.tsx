'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
    Container,
    Loader,
    Alert,
    Stack,
    Text,
    ActionIcon,
    Group,
    Paper,
    Title,
    Button
} from '@mantine/core';
import {
    IconX,
    IconAlertTriangle,
    IconCheck,
    IconClock
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { testApi, TestSessionWithTest } from '@/lib/api';
import { TestPage } from '@/components/test';
import { useAppSelector } from '@/lib/store';

const ClientPage: React.FC = () => {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.id as string;
    const userState = useAppSelector((state) => state.user);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');

    // Check session access
    const {
        data: accessCheck,
        isLoading: accessLoading,
        error: accessError
    } = useQuery({
        queryKey: ['sessionAccess', sessionId],
        queryFn: async () => {
            const result = await testApi.checkSessionAccess(sessionId);
            return result;
        },
        enabled: !!sessionId && !!userState.user,
        retry: 2,
        refetchOnWindowFocus: false,
    });

    // Fetch test session data if can access
    const {
        data: testSession,
        isLoading: sessionLoading,
        error: sessionError,
        refetch
    } = useQuery<TestSessionWithTest>({
        queryKey: ['testSession', sessionId],
        queryFn: async () => {
            const result = await testApi.getTestSession(sessionId);
            return result;
        },
        enabled: !!sessionId && !!userState.user && !!accessCheck?.can_access,
        retry: 2,
        refetchOnWindowFocus: false,
        staleTime: 5 * 60 * 1000,
        gcTime: 10 * 60 * 1000,
    });

    // Redirect if not authenticated
    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
            router.push('/auth/login');
        }
    }, [userState, router]);

    // Connection status handler
    const handleConnectionStatusChange = (status: 'connecting' | 'connected' | 'disconnected') => {
        setConnectionStatus(status);
    };

    // Loading state
    if (accessLoading || (accessCheck?.can_access && sessionLoading)) {
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

    // Error state
    if (accessError || (accessCheck?.can_access && sessionError)) {
        const error = accessError || sessionError;
        return (
            <Container size="md" py="xl">
                <Alert color="red" title="Lỗi" icon={<IconX size={16} />}>
                    <Text mb="md">
                        {(error as any)?.response?.data?.detail || 'Không thể tải bài kiểm tra. Vui lòng thử lại.'}
                    </Text>
                    <Group gap="xs">
                        <Button variant="light" color="blue" onClick={() => refetch()}>
                            Thử lại
                        </Button>
                        <Button variant="light" color="gray" onClick={() => router.back()}>
                            Quay lại
                        </Button>
                    </Group>
                </Alert>
            </Container>
        );
    }

    // Cannot access session - show appropriate message
    if (accessCheck && !accessCheck.can_access) {
        const session = accessCheck.session;

        if (accessCheck.reason === 'test_completed' || accessCheck.reason === 'test_expired') {
            return (
                <Container size="md" py="xl">
                    <Paper p="xl" shadow="sm" withBorder>
                        <Stack align="center" gap="md">
                            {/* Icon based on reason */}
                            <div className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                                {accessCheck.reason === 'test_completed' ? (
                                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                                        <IconCheck size={32} color="green" />
                                    </div>
                                ) : (
                                    <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center">
                                        <IconClock size={32} color="orange" />
                                    </div>
                                )}
                            </div>

                            <Title order={2} ta="center">
                                {accessCheck.reason === 'test_completed'
                                    ? 'Bài kiểm tra đã hoàn thành'
                                    : 'Bài kiểm tra đã hết thời gian'}
                            </Title>

                            <Text ta="center" c="dimmed">
                                {accessCheck.message}
                            </Text>

                            {/* Show results if available */}
                            {session && session.score !== undefined && session.correctAnswers !== undefined && (
                                <div className="bg-gray-50 rounded-lg p-6 w-full">
                                    <Text fw={500} mb="md" ta="center">Kết quả bài kiểm tra</Text>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-blue-600 mb-2">
                                                {Math.round(session.score)}%
                                            </div>
                                            <div className="text-sm text-gray-600">Điểm số</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-green-600 mb-2">
                                                {session.correctAnswers}
                                            </div>
                                            <div className="text-sm text-gray-600">Câu đúng</div>
                                        </div>
                                        <div className="text-center">
                                            <div className="text-2xl font-bold text-gray-600 mb-2">
                                                {testSession?.test?.questions?.length ?? 0}
                                            </div>
                                            <div className="text-sm text-gray-600">Tổng câu hỏi</div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <Group gap="md" mt="md">
                                <Button onClick={() => router.push('/tests')}>
                                    Danh sách bài kiểm tra
                                </Button>
                                {session?.test?.topicId && (
                                    <Button variant="light" onClick={() => router.push(`/topics/${session.test.topicId}`)}>
                                        Quay lại chủ đề
                                    </Button>
                                )}
                            </Group>
                        </Stack>
                    </Paper>
                </Container>
            );
        }

        // Other access denied reasons
        return (
            <Container size="md" py="xl">
                <Alert color="red" title="Không thể truy cập" icon={<IconAlertTriangle size={16} />}>
                    <Text mb="md">{accessCheck.message}</Text>
                    <Group gap="xs">
                        <Button variant="light" color="gray" onClick={() => router.push('/tests')}>
                            Danh sách bài kiểm tra
                        </Button>
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

    // Render test page if can access
    return (
        <TestPage
            sessionId={sessionId}
            onConnectionStatusChange={handleConnectionStatusChange}
        />
    );
};

export default ClientPage; 