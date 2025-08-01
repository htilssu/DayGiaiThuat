'use client';

import React, { useState, useEffect } from 'react';
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
    List,
    ThemeIcon
} from '@mantine/core';
import {
    IconClock,
    IconAlertCircle,
    IconCheck,
    IconArrowRight,
    IconQuestionMark,
    IconBookmark
} from '@tabler/icons-react';
import { useAppSelector } from '@/lib/store';
import { coursesApi } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';

interface EntryTestConfirmClientProps {
    courseId: string;
}

const EntryTestConfirmClient: React.FC<EntryTestConfirmClientProps> = ({ courseId }) => {
    const router = useRouter();
    const userState = useAppSelector(state => state.user);
    const [isStarting, setIsStarting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Validate courseId at component entry
    const courseIdNumber = parseInt(courseId);
    const isCourseIdValid = !isNaN(courseIdNumber) && courseIdNumber > 0 && courseId.trim() !== '';


    // Fetch course information
    const { data: course, isLoading: courseLoading, error: courseError } = useQuery({
        queryKey: ['course', courseId],
        queryFn: async () => {
            return await coursesApi.getCourseById(courseIdNumber);
        },
        enabled: !!courseId && isCourseIdValid,
    });

    // Fetch entry test information
    const { data: entryTest, isLoading: testLoading, error: testError } = useQuery({
        queryKey: ['courseEntryTest', courseId],
        queryFn: async () => {
            return await coursesApi.getCourseEntryTest(courseIdNumber);
        },
        enabled: !!courseId && isCourseIdValid && !!userState.user,
        retry: false, // Don't retry on error to see the actual error
    });



    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
            router.push('/auth/login');
        }
    }, [userState, router]);

    const handleStartTest = async () => {
        if (!userState.user || isStarting || !entryTest || !isCourseIdValid) return;

        try {
            setIsStarting(true);
            setError(null);

            const testSession = await coursesApi.startCourseEntryTest(courseIdNumber);

            router.push(`/tests/${testSession.id}`);
        } catch (err: any) {
            setError(err.message || 'Có lỗi xảy ra khi bắt đầu bài kiểm tra');
            setIsStarting(false);
        }
    };

    const handleCancel = () => {
        if (isCourseIdValid) {
            router.push(`/courses/${courseId}`);
        } else {
            router.push('/courses');
        }
    };

    if (!isCourseIdValid) {
        return (
            <Container size="md" py="xl">
                <Paper p="xl" radius="md" withBorder>
                    <Alert
                        icon={<IconAlertCircle size="1rem" />}
                        title="ID khóa học không hợp lệ"
                        color="red"
                        mb="lg"
                    >
                        ID khóa học "{courseId}" không hợp lệ. Vui lòng kiểm tra lại đường link hoặc chọn khóa học từ danh sách.
                    </Alert>
                    <Button onClick={() => router.push('/courses')}>
                        Quay về danh sách khóa học
                    </Button>
                </Paper>
            </Container>
        );
    }

    if (!userState.user && !userState.isLoading) {
        return null;
    }

    const isLoading = courseLoading || testLoading;
    const hasError = courseError || testError;

    if (isLoading) {
        return (
            <Container size="md" py="xl">
                <Paper p="xl" radius="md" withBorder>
                    <Group justify="center">
                        <Loader size="lg" />
                        <Text>Đang tải thông tin bài kiểm tra...</Text>
                    </Group>
                </Paper>
            </Container>
        );
    }

    if (hasError || !course) {
        return (
            <Container size="md" py="xl">
                <Paper p="xl" radius="md" withBorder>
                    <Alert
                        icon={<IconAlertCircle size="1rem" />}
                        title="Lỗi"
                        color="red"
                        mb="lg"
                    >
                        {testError ? `Không thể tải thông tin bài kiểm tra: ${JSON.stringify(testError)}` :
                            courseError ? `Không thể tải thông tin khóa học: ${JSON.stringify(courseError)}` :
                                'Vui lòng thử lại sau.'}
                    </Alert>
                    <Button variant='outline' onClick={() => router.push('/courses')}>
                        Quay về danh sách khóa học
                    </Button>
                </Paper>
            </Container>
        );
    }

    if (!entryTest) {
        return (
            <Container size="md" py="xl">
                <Paper p="xl" radius="md" withBorder>
                    <Alert
                        icon={<IconAlertCircle size="1rem" />}
                        title="Không có bài kiểm tra đầu vào"
                        color="yellow"
                        mb="lg"
                    >
                        Khóa học này chưa có bài kiểm tra đầu vào. Bạn có thể bắt đầu học ngay.
                    </Alert>
                    <Button onClick={() => router.push(`/courses/${courseId}`)}>
                        Bắt đầu học khóa học
                    </Button>
                </Paper>
            </Container>
        );
    }

    // Tính toán thời gian làm bài (phút) và số câu hỏi
    const durationMinutes = entryTest.durationMinutes || 45;
    const questionCount = entryTest.questions?.length || 0;

    return (
        <Container size="md" py="xl">
            <Paper p="xl" radius="md" withBorder>
                <Stack gap="lg">
                    <div>
                        <Title order={2} mb="xs">
                            Bài kiểm tra đầu vào
                        </Title>
                        <Text c="dimmed" size="lg">
                            {course.title}
                        </Text>
                    </div>

                    {error && (
                        <Alert
                            icon={<IconAlertCircle size="1rem" />}
                            title="Lỗi"
                            color="red"
                        >
                            {error}
                        </Alert>
                    )}

                    <Paper p="md" bg="blue.0" radius="md">
                        <Title order={4} mb="md" c="blue.7">
                            <ThemeIcon variant="light" color="blue" size="sm" mr="xs">
                                <IconBookmark size="1rem" />
                            </ThemeIcon>
                            Thông tin bài kiểm tra
                        </Title>

                        <List
                            spacing="sm"
                            size="sm"
                            icon={
                                <ThemeIcon color="blue" size={20} radius="xl">
                                    <IconCheck size="0.8rem" />
                                </ThemeIcon>
                            }
                        >
                            <List.Item>
                                <Group gap="xs">
                                    <IconClock size="1rem" />
                                    <Text>Thời gian: {durationMinutes} phút</Text>
                                </Group>
                            </List.Item>
                            <List.Item>
                                <Group gap="xs">
                                    <IconQuestionMark size="1rem" />
                                    <Text>Số câu hỏi: {questionCount > 0 ? `${questionCount} câu` : 'Khoảng 15-20 câu'}</Text>
                                </Group>
                            </List.Item>
                            <List.Item>
                                <Text>Gồm câu hỏi trắc nghiệm và bài tập lập trình</Text>
                            </List.Item>
                            <List.Item>
                                <Text>Đánh giá kiến thức nền tảng của bạn</Text>
                            </List.Item>
                        </List>
                    </Paper>

                    <Alert
                        icon={<IconAlertCircle size="1rem" />}
                        title="Lưu ý quan trọng"
                        color="yellow"
                    >
                        <List size="sm" spacing="xs">
                            <List.Item>Bạn chỉ có thể làm bài kiểm tra này một lần</List.Item>
                            <List.Item>Khi bắt đầu, thời gian sẽ được tính ngay lập tức</List.Item>
                            <List.Item>Đảm bảo kết nối internet ổn định trong suốt quá trình làm bài</List.Item>
                            <List.Item>Nếu thoát giữa chừng, bạn vẫn có thể tiếp tục làm bài từ vị trí cũ</List.Item>
                        </List>
                    </Alert>

                    <Group justify="center" mt="xl">
                        <Button
                            variant="outline"
                            size="md"
                            onClick={handleCancel}
                            disabled={isStarting}
                        >
                            Hủy bỏ
                        </Button>
                        <Button
                            size="md"
                            rightSection={<IconArrowRight size="1rem" />}
                            onClick={handleStartTest}
                            loading={isStarting}
                            disabled={isStarting || !entryTest}
                        >
                            {isStarting ? 'Đang tạo bài kiểm tra...' : 'Bắt đầu làm bài'}
                        </Button>
                    </Group>
                </Stack>
            </Paper>
        </Container>
    );
};

export default EntryTestConfirmClient; 