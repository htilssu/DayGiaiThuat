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

const ClientPage: React.FC = () => {
    const router = useRouter();
    const searchParams = useSearchParams();
    const userState = useAppSelector((state) => state.user);
    const [startingTest, setStartingTest] = useState<number | null>(null);
    const [activeTab, setActiveTab] = useState<string>('available');

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

    // Lấy entry tests từ các khóa học đã đăng ký
    const {
        data: courseTests,
        isLoading: testsLoading,
        error: testsError,
        refetch: refetchTests
    } = useQuery({
        queryKey: ['courseTests', enrolledCourses],
        queryFn: async () => {
            if (!enrolledCourses || enrolledCourses.length === 0) {
                return [];
            }

            const testPromises = enrolledCourses.map(async (course) => {
                try {
                    const entryTest = await coursesApi.getCourseEntryTest(course.id);
                    return {
                        ...entryTest,
                        courseTitle: course.title,
                        courseId: course.id,
                        courseThumbnail: course.thumbnailUrl,
                        courseLevel: course.level
                    };
                } catch (error: any) {
                    // Nếu course không có entry test thì return null
                    if (error.response?.status === 404) {
                        return null;
                    }
                    console.error(`Error fetching entry test for course ${course.id}:`, error);
                    return null;
                }
            });

            const results = await Promise.all(testPromises);
            return results.filter(test => test !== null);
        },
        enabled: !!enrolledCourses && enrolledCourses.length > 0,
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

    const handleStartTest = async (testId: number) => {
        if (!userState.user || startingTest) return;

        try {
            setStartingTest(testId);

            // Kiểm tra xem có thể làm bài kiểm tra không
            const canTake = await testApi.canTakeTest(testId);

            if (!canTake.canTake) {
                alert(canTake.reason || 'Không thể làm bài kiểm tra này');
                return;
            }

            // Tạo test session mới
            const session = await testApi.createTestSession({
                testId: testId
            });

            // Chuyển hướng đến trang làm bài
            router.push(`/tests/${session.id}`);
        } catch (error: any) {
            console.error('Error starting test:', error);
            alert('Có lỗi xảy ra khi bắt đầu bài kiểm tra. Vui lòng thử lại.');
        } finally {
            setStartingTest(null);
        }
    };

    const handleStartEntryTest = (courseId: number) => {
        router.push(`/tests/entry/${courseId}`);
    };

    const handleViewResult = (sessionId: string) => {
        router.push(`/tests/${sessionId}`);
    };

    const getDifficultyColor = (level: string) => {
        switch (level.toLowerCase()) {
            case 'easy':
            case 'dễ':
            case 'beginner':
                return 'green';
            case 'medium':
            case 'trung bình':
            case 'intermediate':
                return 'yellow';
            case 'hard':
            case 'khó':
            case 'advanced':
                return 'red';
            default:
                return 'blue';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'green';
            case 'expired':
                return 'orange';
            case 'in_progress':
                return 'blue';
            default:
                return 'gray';
        }
    };

    const getStatusLabel = (status: string, isSubmitted: boolean) => {
        if (status === 'completed' && isSubmitted) return 'Hoàn thành';
        if (status === 'expired') return 'Hết thời gian';
        if (status === 'in_progress') return 'Đang làm';
        return 'Chưa xác định';
    };

    const formatDuration = (minutes: number) => {
        if (minutes < 60) {
            return `${minutes} phút`;
        }
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return remainingMinutes > 0
            ? `${hours}h ${remainingMinutes}m`
            : `${hours} giờ`;
    };

    const formatDate = (dateString: string | null | undefined) => {
        if (!dateString) {
            return 'Chưa bắt đầu';
        }
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Thời gian không hợp lệ';
            }
            return date.toLocaleString('vi-VN', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return 'Thời gian không hợp lệ';
        }
    };

    const formatTestDuration = (minutes: number) => {
        if (minutes < 60) {
            return `${minutes} phút`;
        }
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours} giờ`;
    };

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

    const isLoading = coursesLoading || testsLoading || historyLoading;
    const error = coursesError || testsError || historyError;

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
                            refetchTests();
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
                <Tabs value={activeTab} onChange={(value) => setActiveTab(value || 'available')}>
                    <Tabs.List>
                        <Tabs.Tab value="available" leftSection={<IconQuestionMark size={16} />}>
                            Bài kiểm tra đầu vào ({courseTests?.length || 0})
                        </Tabs.Tab>
                        <Tabs.Tab value="history" leftSection={<IconHistory size={16} />}>
                            Lịch sử làm bài ({testHistory?.length || 0})
                        </Tabs.Tab>
                    </Tabs.List>

                    {/* Available Tests Tab */}
                    <Tabs.Panel value="available" pt="md">
                        {courseTests && courseTests.length > 0 ? (
                            <Grid gutter="md">
                                {courseTests.map((test: any) => (
                                    <Grid.Col key={test.id} span={{ base: 12, md: 6, lg: 4 }}>
                                        <Card shadow="sm" padding="lg" radius="md" withBorder h="100%">
                                            <Stack gap="md" h="100%" justify="space-between">
                                                {/* Test Header */}
                                                <Stack gap="xs">
                                                    <Group justify="space-between" align="flex-start">
                                                        <ThemeIcon size="lg" variant="light" color="blue">
                                                            <IconQuestionMark size={20} />
                                                        </ThemeIcon>
                                                        <Badge
                                                            color={getDifficultyColor(test.courseLevel || 'medium')}
                                                            variant="light"
                                                            size="sm"
                                                        >
                                                            {test.courseLevel || 'Trung bình'}
                                                        </Badge>
                                                    </Group>

                                                    <Title order={4} lineClamp={2}>
                                                        Bài kiểm tra đầu vào
                                                    </Title>

                                                    <Text fw={500} size="sm" c="blue.6">
                                                        {test.courseTitle}
                                                    </Text>
                                                </Stack>

                                                <Divider />

                                                {/* Test Info */}
                                                <Stack gap="xs">
                                                    <Group gap="xs" justify="space-between">
                                                        <Group gap="xs">
                                                            <IconClock size={16} color="gray" />
                                                            <Text size="sm" c="dimmed">
                                                                {formatDuration(test.durationMinutes || 45)}
                                                            </Text>
                                                        </Group>
                                                        <Group gap="xs">
                                                            <IconQuestionMark size={16} color="gray" />
                                                            <Text size="sm" c="dimmed">
                                                                {test.questions ? test.questions.length : '15-20'} câu
                                                            </Text>
                                                        </Group>
                                                    </Group>

                                                    <Group gap="xs">
                                                        <IconBook size={16} color="gray" />
                                                        <Text size="sm" c="dimmed" lineClamp={1}>
                                                            Đánh giá kiến thức nền tảng
                                                        </Text>
                                                    </Group>
                                                </Stack>

                                                <Divider />

                                                {/* Action Button */}
                                                <Button
                                                    fullWidth
                                                    leftSection={<IconPlayerPlay size={16} />}
                                                    rightSection={<IconChevronRight size={16} />}
                                                    variant="filled"
                                                    onClick={() => handleStartEntryTest(test.courseId)}
                                                >
                                                    Bắt đầu làm bài
                                                </Button>
                                            </Stack>
                                        </Card>
                                    </Grid.Col>
                                ))}
                            </Grid>
                        ) : (
                            <Paper p="xl" withBorder>
                                <Stack align="center" gap="md">
                                    <ThemeIcon size="xl" variant="light" color="gray">
                                        <IconQuestionMark size={32} />
                                    </ThemeIcon>
                                    <Title order={3} ta="center">Chưa có bài kiểm tra đầu vào</Title>
                                    <Text c="dimmed" ta="center">
                                        {enrolledCourses && enrolledCourses.length === 0
                                            ? 'Bạn chưa đăng ký khóa học nào. Hãy đăng ký khóa học để truy cập bài kiểm tra.'
                                            : 'Các khóa học bạn đã đăng ký chưa có bài kiểm tra đầu vào.'
                                        }
                                    </Text>
                                    <Button
                                        variant="light"
                                        onClick={() => router.push('/courses')}
                                        leftSection={<IconBook size={16} />}
                                    >
                                        Xem khóa học
                                    </Button>
                                </Stack>
                            </Paper>
                        )}
                    </Tabs.Panel>

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
                                            <Table.Tr key={session.sessionId}>
                                                <Table.Td>
                                                    <Stack gap={2}>
                                                        <Text fw={500} size="sm">
                                                            {session.testName}
                                                        </Text>
                                                    </Stack>
                                                </Table.Td>
                                                <Table.Td>
                                                    <Badge
                                                        color={getStatusColor(session.status)}
                                                        variant="light"
                                                        leftSection={
                                                            session.status === 'completed' ? <IconCheck size={12} /> :
                                                                session.status === 'expired' ? <IconClockHour9 size={12} /> :
                                                                    <IconX size={12} />
                                                        }
                                                    >
                                                        {getStatusLabel(session.status, true)}
                                                    </Badge>
                                                </Table.Td>
                                                <Table.Td>
                                                    <Group gap="xs">
                                                        <IconClock size={14} color="gray" />
                                                        <Text size="sm">
                                                            {formatTestDuration(session.durationMinutes)}
                                                        </Text>
                                                    </Group>
                                                </Table.Td>
                                                <Table.Td>
                                                    {session.score !== null && session.score !== undefined ? (
                                                        <Group gap="xs">
                                                            <IconTrophy size={14} color="gold" />
                                                            <Text size="sm" fw={500} c={
                                                                session.score >= 80 ? 'green' :
                                                                    session.score >= 60 ? 'orange' : 'red'
                                                            }>
                                                                {Math.round(session.score)}%
                                                            </Text>
                                                        </Group>
                                                    ) : (
                                                        <Text size="sm" c="dimmed">-</Text>
                                                    )}
                                                </Table.Td>
                                                <Table.Td>
                                                    {session.correctAnswers !== null && session.correctAnswers !== undefined ? (
                                                        <Group gap="xs">
                                                            <IconTarget size={14} color="green" />
                                                            <Text size="sm">
                                                                {session.correctAnswers}/{session.totalQuestions}
                                                            </Text>
                                                        </Group>
                                                    ) : (
                                                        <Text size="sm" c="dimmed">-</Text>
                                                    )}
                                                </Table.Td>
                                                <Table.Td>
                                                    <Group gap="xs">
                                                        <IconCalendar size={14} color="gray" />
                                                        <Text size="sm">
                                                            {formatDate(session.startTime)}
                                                        </Text>
                                                    </Group>
                                                </Table.Td>
                                                <Table.Td>
                                                    <Button
                                                        size="xs"
                                                        variant="light"
                                                        onClick={() => handleViewResult(session.sessionId)}
                                                    >
                                                        Xem kết quả
                                                    </Button>
                                                </Table.Td>
                                            </Table.Tr>
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