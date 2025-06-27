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
    Paper
} from '@mantine/core';
import {
    IconX,
    IconAlertTriangle
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

    // Debug logging
    useEffect(() => {
    }, [sessionId, userState]);

    // Fetch test session data - chỉ để validate session exists
    const {
        data: testSession,
        isLoading,
        error,
        refetch
    } = useQuery<TestSessionWithTest>({
        queryKey: ['testSessionValidation', sessionId],
        queryFn: async () => {
            try {
                const result = await testApi.getTestSession(sessionId);
                return result;
            } catch (err) {
                throw err;
            }
        },
        enabled: !!sessionId && !!userState.user,
        retry: 2,
        refetchOnWindowFocus: false, // Ngăn refetch khi chuyển tab
        staleTime: 5 * 60 * 1000, // 5 phút - dữ liệu không bị stale
        gcTime: 10 * 60 * 1000, // 10 phút cache (gcTime thay cho cacheTime trong v5)
    });

    // Debug logging for query state
    useEffect(() => {

    }, [isLoading, error, testSession]);

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

    // Chỉ render TestPage với callback để xử lý connection status
    return (
        <TestPage
            sessionId={sessionId}
            onConnectionStatusChange={handleConnectionStatusChange}
        />
    );
};

export default ClientPage; 