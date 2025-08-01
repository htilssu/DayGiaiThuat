'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import {
    Container,
    Title,
    Grid,
    Card,
    Text,
    Button,
    Badge,
    Group,
    Stack,
    Paper,
    ActionIcon,
    Loader,
    Alert,
    ThemeIcon,
    Divider,
    Tabs,
    Progress,
    Table,
    ScrollArea
} from '@mantine/core';
import {
    IconClock,
    IconQuestionMark,
    IconPlayerPlay,
    IconTrophy,
    IconBook,
    IconChevronRight,
    IconAlertCircle,
    IconRefresh,
    IconHistory,
    IconTarget,
    IconCalendar,
    IconCheck,
    IconX,
    IconClockHour9
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { testApi, TestHistorySummary, coursesApi, EnrolledCourse } from '@/lib/api';
import { useAppSelector } from '@/lib/store';
import TestSessionHistoryRow from './TestSessionHistoryRow';

const ClientPage: React.FC = () => {
    const router = useRouter();
    const searchParams = useSearchParams();
    const userState = useAppSelector((state) => state.user);
    const [startingTest, setStartingTest] = useState<number | null>(null);
    const [activeTab, setActiveTab] = useState<string>('history');

    // Handle authentication redirect
    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
            // Store current URL for redirect after login
            const currentUrl = window.location.pathname + window.location.search;
            router.push(`/auth/login?redirect=${encodeURIComponent(currentUrl)}`);
            return;
        }
    }, [userState, router]);

    // Lấy danh sách khóa học đã đăng ký
    const {
        data: enrolledCourses,
        isLoading: coursesLoading,
        error: coursesError,
        refetch: refetchCourses
    } = useQuery({
        queryKey: ['enrolledCourses'],
        queryFn: () => coursesApi.getEnrolledCourses(),
        enabled: !!userState.user,
    });


    // Lấy lịch sử làm bài
    const {
        data: testHistory,
        isLoading: historyLoading,
        error: historyError,
        refetch: refetchHistory
    } = useQuery({
        queryKey: ['testHistory'],
        queryFn: () => testApi.getUserTestHistory(),
        enabled: !!userState.user,
    });


    // Show loading while checking authentication
    if (userState.isLoading || userState.isInitial) {
        return (
            <Container size="lg" py="xl">
                <Stack align="center" gap="md">
                    <Loader size="lg" />
                    <Text>Đang kiểm tra thông tin đăng nhập...</Text>
                </Stack>
            </Container>
        );
    }

    // If user is not logged in, show login required message
    if (!userState.user) {
        return (
            <Container size="md" py="xl">
                <Alert color="orange" title="Yêu cầu đăng nhập" icon={<IconAlertCircle size={16} />}>
                    <Text mb="md">Bạn cần đăng nhập để xem danh sách bài kiểm tra.</Text>
                    <Button onClick={() => router.push('/auth/login')}>
                        Đăng nhập
                    </Button>
                </Alert>
            </Container>
        );
    }

    const isLoading = coursesLoading || historyLoading;
    const error = coursesError || historyError;

    if (isLoading) {
        return (
            <Container size="lg" py="xl">
                <Stack align="center" gap="md">
                    <Loader size="lg" />
                    <Text>Đang tải danh sách bài kiểm tra...</Text>
                </Stack>
            </Container>
        );
    }

    if (error) {
        return (
            <Container size="md" py="xl">
                <Alert color="red" title="Có lỗi xảy ra" icon={<IconAlertCircle size={16} />}>
                    <Text mb="md">
                        Không thể tải danh sách bài kiểm tra. Vui lòng thử lại.
                    </Text>
                    <Group gap="xs">
                        <Button variant="light" leftSection={<IconRefresh size={16} />} onClick={() => {
                            refetchCourses();
                            refetchHistory();
                        }}>
                            Thử lại
                        </Button>
                    </Group>
                </Alert>
            </Container>
        );
    }

    return (
        <Container size="lg" py="xl">
            <Stack gap="xl">
                {/* Header */}
                <div>
                    <Title order={1} mb="xs">Bài Kiểm Tra</Title>
                    <Text c="dimmed" size="lg">
                        Quản lý và theo dõi quá trình làm bài kiểm tra từ các khóa học bạn đã đăng ký
                    </Text>
                </div>

                {/* Enrolled Courses Summary */}
                {enrolledCourses && enrolledCourses.length > 0 && (
                    <Paper p="md" bg="blue.0" radius="md">
                        <Group justify="space-between" align="center">
                            <Group gap="xs">
                                <ThemeIcon size="lg" variant="light" color="blue">
                                    <IconBook size={20} />
                                </ThemeIcon>
                                <div>
                                    <Text fw={500}>Khóa học đã đăng ký</Text>
                                    <Text size="sm" c="dimmed">
                                        Bạn đã đăng ký {enrolledCourses.length} khóa học
                                    </Text>
                                </div>
                            </Group>
                            <Button
                                variant="light"
                                size="sm"
                                onClick={() => router.push('/courses')}
                            >
                                Xem tất cả
                            </Button>
                        </Group>
                    </Paper>
                )}

                {/* Tabs */}
                <Tabs value={activeTab} onChange={(value) => setActiveTab(value || 'history')}>
                    <Tabs.List>
                        <Tabs.Tab value="history" leftSection={<IconHistory size={16} />}>
                            Lịch sử làm bài ({testHistory?.length || 0})
                        </Tabs.Tab>
                    </Tabs.List>


                    {/* Test History Tab */}
                    <Tabs.Panel value="history" pt="md">
                        {testHistory && testHistory.length > 0 ? (
                            <ScrollArea>
                                <Table striped highlightOnHover>
                                    <Table.Thead>
                                        <Table.Tr>
                                            <Table.Th>Bài kiểm tra</Table.Th>
                                            <Table.Th>Trạng thái</Table.Th>
                                            <Table.Th>Thời gian làm</Table.Th>
                                            <Table.Th>Điểm số</Table.Th>
                                            <Table.Th>Số câu đúng</Table.Th>
                                            <Table.Th>Ngày làm</Table.Th>
                                            <Table.Th>Hành động</Table.Th>
                                        </Table.Tr>
                                    </Table.Thead>
                                    <Table.Tbody>
                                        {testHistory.map((session: TestHistorySummary) => (
                                            <TestSessionHistoryRow key={session.sessionId} session={session} />
                                        ))}
                                    </Table.Tbody>
                                </Table>
                            </ScrollArea>
                        ) : (
                            <Paper p="xl" withBorder>
                                <Stack align="center" gap="md">
                                    <ThemeIcon size="xl" variant="light" color="gray">
                                        <IconHistory size={32} />
                                    </ThemeIcon>
                                    <Title order={3} ta="center">Chưa có lịch sử làm bài</Title>
                                    <Text c="dimmed" ta="center">
                                        Bạn chưa hoàn thành bài kiểm tra nào. Hãy chuyển sang tab "Bài kiểm tra đầu vào" để bắt đầu.
                                    </Text>
                                    <Button
                                        variant="light"
                                        onClick={() => setActiveTab('available')}
                                        leftSection={<IconQuestionMark size={16} />}
                                    >
                                        Xem bài kiểm tra đầu vào
                                    </Button>
                                </Stack>
                            </Paper>
                        )}
                    </Tabs.Panel>
                </Tabs>
            </Stack>
        </Container>
    );
};

export default ClientPage; 