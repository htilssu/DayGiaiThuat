'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
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
    Divider
} from '@mantine/core';
import {
    IconClock,
    IconQuestionMark,
    IconPlayerPlay,
    IconTrophy,
    IconBook,
    IconChevronRight,
    IconAlertCircle,
    IconRefresh
} from '@tabler/icons-react';
import { useQuery } from '@tanstack/react-query';
import { testApi } from '@/lib/api';
import { useAppSelector } from '@/lib/store';

const ClientPage: React.FC = () => {
    const router = useRouter();
    const userState = useAppSelector((state) => state.user);
    const [startingTest, setStartingTest] = useState<number | null>(null);

    const {
        data: tests,
        isLoading,
        error,
        refetch
    } = useQuery({
        queryKey: ['tests'],
        queryFn: () => testApi.getTests(),
        enabled: !!userState.user,
    });

    const handleStartTest = async (testId: number) => {
        if (!userState.user || startingTest) return;

        try {
            setStartingTest(testId);

            // Tạo test session mới
            const session = await testApi.createTestSession({
                test_id: testId,
                user_id: userState.user.id
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

    const getDifficultyColor = (level: string) => {
        switch (level.toLowerCase()) {
            case 'easy':
            case 'dễ':
                return 'green';
            case 'medium':
            case 'trung bình':
                return 'yellow';
            case 'hard':
            case 'khó':
                return 'red';
            default:
                return 'blue';
        }
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
                        <ActionIcon variant="light" color="blue" onClick={() => refetch()}>
                            <IconRefresh size={16} />
                        </ActionIcon>
                        <Button variant="light" leftSection={<IconRefresh size={16} />} onClick={() => refetch()}>
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
                    <Title order={1} mb="xs">Danh Sách Bài Kiểm Tra</Title>
                    <Text c="dimmed" size="lg">
                        Chọn bài kiểm tra để đánh giá kiến thức và kỹ năng của bạn
                    </Text>
                </div>

                {/* Tests Grid */}
                {tests && tests.length > 0 ? (
                    <Grid gutter="md">
                        {tests.map((test: any) => (
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
                                                    color={getDifficultyColor(test.difficulty || 'medium')}
                                                    variant="light"
                                                    size="sm"
                                                >
                                                    {test.difficulty || 'Trung bình'}
                                                </Badge>
                                            </Group>

                                            <Title order={4} lineClamp={2}>
                                                {test.name || `Bài kiểm tra ${test.id}`}
                                            </Title>

                                            {test.description && (
                                                <Text c="dimmed" size="sm" lineClamp={3}>
                                                    {test.description}
                                                </Text>
                                            )}
                                        </Stack>

                                        <Divider />

                                        {/* Test Info */}
                                        <Stack gap="xs">
                                            <Group gap="xs" justify="space-between">
                                                <Group gap="xs">
                                                    <IconClock size={16} color="gray" />
                                                    <Text size="sm" c="dimmed">
                                                        {formatDuration(test.duration_minutes || 60)}
                                                    </Text>
                                                </Group>
                                                <Group gap="xs">
                                                    <IconQuestionMark size={16} color="gray" />
                                                    <Text size="sm" c="dimmed">
                                                        {test.questions ? Object.keys(test.questions).length : '?'} câu
                                                    </Text>
                                                </Group>
                                            </Group>

                                            {test.topic_name && (
                                                <Group gap="xs">
                                                    <IconBook size={16} color="gray" />
                                                    <Text size="sm" c="dimmed" lineClamp={1}>
                                                        {test.topic_name}
                                                    </Text>
                                                </Group>
                                            )}
                                        </Stack>

                                        <Divider />

                                        {/* Action Button */}
                                        <Button
                                            fullWidth
                                            leftSection={startingTest === test.id ? <Loader size={16} /> : <IconPlayerPlay size={16} />}
                                            rightSection={<IconChevronRight size={16} />}
                                            variant="filled"
                                            loading={startingTest === test.id}
                                            onClick={() => handleStartTest(test.id)}
                                            disabled={!!startingTest}
                                        >
                                            {startingTest === test.id ? 'Đang bắt đầu...' : 'Bắt đầu làm bài'}
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
                            <Title order={3} ta="center">Chưa có bài kiểm tra nào</Title>
                            <Text c="dimmed" ta="center">
                                Hiện tại chưa có bài kiểm tra nào khả dụng. Vui lòng quay lại sau.
                            </Text>
                        </Stack>
                    </Paper>
                )}
            </Stack>
        </Container>
    );
};

export default ClientPage; 