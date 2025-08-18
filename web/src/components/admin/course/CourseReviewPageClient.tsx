"use client";

import {
    Container,
    Grid,
    Card,
    Title,
    Text,
    Button,
    Group,
    Badge,
    LoadingOverlay,
    Alert,
    Stack,
    Divider,
    Paper,
    ActionIcon,
    Tooltip,
} from "@mantine/core";
import { useState, useEffect } from "react";
import { IconCheck, IconX, IconRefresh, IconAlertCircle, IconRobot } from "@tabler/icons-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { notifications } from '@mantine/notifications';
import { useRouter } from "next/navigation";
import { getCourseTopicsReview } from "@/lib/api/course-topics-review";
import { CourseTopicsReview } from "@/types/course-review";

interface CourseReviewPageClientProps {
    courseId: string;
}

export default function CourseReviewPageClient({ courseId }: CourseReviewPageClientProps) {
    const router = useRouter();

    // Fetch course review data from API
    const { data: reviewData, isLoading, error, refetch } = useQuery<CourseTopicsReview>({
        queryKey: ['courseReview', courseId],
        queryFn: () => getCourseTopicsReview(parseInt(courseId)),
        retry: 1,
    });

    const handleApproveContent = () => {
        // Chuyển hướng đến trang review topics thay vì approve trực tiếp
        router.push(`/admin/course/${courseId}/review-topics`);
    };

    const handleRejectContent = () => {
        // Có thể implement feedback sau hoặc chuyển hướng đến trang khác
        notifications.show({
            title: 'Thông báo',
            message: 'Tính năng reject sẽ được implement sau',
            color: 'blue',
        });
    };

    const handleRegenerateContent = () => {
        refetch();
    };

    if (isLoading) {
        return (
            <Container size="xl" py="xl">
                <LoadingOverlay visible />
                <Text ta="center" mt="xl">Đang tải thông tin review...</Text>
            </Container>
        );
    }

    if (error || !reviewData) {
        return (
            <Container size="xl" py="xl">
                <Alert icon={<IconAlertCircle size={16} />} title="Lỗi" color="red">
                    {error?.message || 'Không thể tải thông tin review khóa học'}
                </Alert>
            </Container>
        );
    }

    return (
        <Container size="xl" py="xl">
            <Grid>
                {/* Left Column - Course Info & Generated Content */}
                <Grid.Col span={12}>
                    <Stack gap="lg">
                        {/* Course Basic Info */}
                        <Card withBorder shadow="sm" p="lg">
                            <Group justify="space-between" mb="md">
                                <Title order={2} c="blue">Thông tin khóa học</Title>
                                <Badge
                                    color="blue"
                                    size="lg"
                                >
                                    Topics đã tạo
                                </Badge>
                            </Group>

                            <Stack gap="sm">
                                <Text size="lg" fw={500}>Khóa học ID: {reviewData.courseId}</Text>
                                <Text size="sm" c="dimmed">{reviewData.description}</Text>
                                <Text size="sm" c="dimmed">Course ID: {reviewData.courseId}</Text>
                                <Text size="sm" c="dimmed">
                                    Session ID: {reviewData.sessionId}
                                </Text>
                            </Stack>
                        </Card>

                        {/* Generated Content */}
                        <Card withBorder shadow="sm" p="lg">
                            <Group justify="space-between" mb="md">
                                <Title order={2} c="violet">
                                    <Group gap="xs">
                                        <IconRobot size={24} />
                                        Nội dung do Agent tạo
                                    </Group>
                                </Title>
                                <Group>
                                    <Tooltip label="Tải lại nội dung">
                                        <ActionIcon
                                            variant="light"
                                            color="blue"
                                            onClick={handleRegenerateContent}
                                        >
                                            <IconRefresh size={16} />
                                        </ActionIcon>
                                    </Tooltip>
                                </Group>
                            </Group>

                            {!reviewData.topics || reviewData.topics.length === 0 ? (
                                <Paper withBorder p="xl" style={{ textAlign: 'center' }}>
                                    <Stack gap="md" align="center">
                                        <IconRobot size={48} style={{ color: 'var(--mantine-color-violet-6)' }} />
                                        <Text size="lg" fw={500}>Đang tạo nội dung khóa học...</Text>
                                        <Text size="sm" c="dimmed">
                                            AI Agent đang phân tích và tạo nội dung cho khóa học này.
                                            Vui lòng chờ trong giây lát.
                                        </Text>
                                    </Stack>
                                </Paper>
                            ) : (
                                <Stack gap="md">
                                    {/* Topics */}
                                    {reviewData.topics && reviewData.topics.length > 0 && (
                                        <Paper withBorder p="md">
                                            <Title order={4} mb="sm">Topics ({reviewData.topics.length})</Title>
                                            <Stack gap="xs">
                                                {reviewData.topics.map((topic, index) => (
                                                    <Group key={topic.id} justify="space-between">
                                                        <div>
                                                            <Text fw={500}>{topic.name}</Text>
                                                            <Text size="sm" c="dimmed">{topic.description}</Text>
                                                            {topic.skills && topic.skills.length > 0 && (
                                                                <Text size="xs" c="blue" mt={2}>
                                                                    {topic.skills.length} kỹ năng
                                                                </Text>
                                                            )}
                                                        </div>
                                                    </Group>
                                                ))}
                                            </Stack>
                                        </Paper>
                                    )}
                                </Stack>
                            )}

                            <Divider />

                            {/* Action Buttons */}
                            {reviewData.topics && reviewData.topics.length > 0 && (
                                <Group justify="center" mt={20}>

                                    <Button
                                        color="green"
                                        leftSection={<IconCheck size={16} />}
                                        onClick={handleApproveContent}
                                    >
                                        Chuyển sang Review Topics
                                    </Button>
                                </Group>
                            )}
                        </Card>
                    </Stack>
                </Grid.Col>
            </Grid>
        </Container>
    );
}
