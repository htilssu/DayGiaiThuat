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

    // Fetch test session data
    const {
        data: testSession,
        isLoading,
        error,
        refetch
    } = useQuery({
        queryKey: ['testSession', sessionId],
        queryFn: () => testApi.getTestSession(parseInt(sessionId)),
        enabled: !!sessionId && !!userState.user,
        retry: 2,
        refetchOnWindowFocus: false,
    });

    // Redirect if not authenticated
    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
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
                        </Group>
                        {testSession.test && (
                            <Text c="dimmed" size="sm">
                                Câu hỏi: {testSession.test.questions.length} •
                                Thời gian: {testSession.test.duration} phút
                            </Text>
                        )}
                    </Stack>

                    <Stack gap={4} align="end">
                        <Group gap="xs" align="center">
                            <IconClock size={16} />
                            <Text fw={500}>
                                {formatTimeRemaining(testSession.time_remaining_seconds)}
                            </Text>
                        </Group>
                        <Text c="dimmed" size="sm">
                            Trạng thái: {testSession.status}
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
            </Paper>

            {/* Test content */}
            <TestPage
                sessionId={parseInt(sessionId)}
                onConnectionStatusChange={setConnectionStatus}
            />
        </Container>
    );
};

export default ClientPage; 