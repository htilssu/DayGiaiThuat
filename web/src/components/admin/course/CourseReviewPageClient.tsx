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
import { IconCheck, IconX, IconRefresh, IconAlertCircle, IconMessageCircle, IconRobot } from "@tabler/icons-react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { notifications } from '@mantine/notifications';
import { useRouter } from "next/navigation";
import AdminChat from "@/components/Chat/AdminChat";
import { getCourseReview, approveRejectCourse, CourseReview } from "@/lib/api/admin-courses";

interface CourseReviewPageClientProps {
    courseId: string;
}

export default function CourseReviewPageClient({ courseId }: CourseReviewPageClientProps) {
    const [showChat, setShowChat] = useState(false);
    const router = useRouter();

    // Fetch course review data from API
    const { data: reviewData, isLoading, error, refetch } = useQuery<CourseReview>({
        queryKey: ['courseReview', courseId],
        queryFn: () => getCourseReview(parseInt(courseId)),
        retry: 1,
    });

    // Mutation for approve/reject
    const approveRejectMutation = useMutation({
        mutationFn: (action: 'approve' | 'reject') =>
            approveRejectCourse(parseInt(courseId), { action }),
        onSuccess: (data) => {
            notifications.show({
                title: 'Thành công',
                message: data.message,
                color: 'green',
            });
            router.push('/admin/course');
        },
        onError: (error: any) => {
            notifications.show({
                title: 'Lỗi',
                message: error.message || 'Có lỗi xảy ra',
                color: 'red',
            });
        },
    });

    const handleApproveContent = () => {
        approveRejectMutation.mutate('approve');
    };

    const handleRejectContent = () => {
        approveRejectMutation.mutate('reject');
        setShowChat(true);
        notifications.show({
            title: 'Nội dung bị từ chối',
            message: 'Hãy chat với AI để yêu cầu tạo lại nội dung',
            color: 'orange',
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
                <Grid.Col span={showChat ? 8 : 12}>
                    <Stack gap="lg">
                        {/* Course Basic Info */}
                        <Card withBorder shadow="sm" p="lg">
                            <Group justify="space-between" mb="md">
                                <Title order={2} c="blue">Thông tin khóa học</Title>
                                <Badge
                                    color={
                                        reviewData.draft?.status === 'approved' ? 'green' :
                                            reviewData.draft?.status === 'rejected' ? 'red' :
                                                reviewData.draft?.status === 'reviewing' ? 'yellow' : 'gray'
                                    }
                                    size="lg"
                                >
                                    {reviewData.draft ? (
                                        reviewData.draft.status === 'approved' ? 'Đã duyệt' :
                                            reviewData.draft.status === 'rejected' ? 'Bị từ chối' :
                                                reviewData.draft.status === 'reviewing' ? 'Đang review' : 'Nháp'
                                    ) : 'Đang tạo'}
                                </Badge>
                            </Group>

                            <Stack gap="sm">
                                <Text size="lg" fw={500}>{reviewData.courseTitle}</Text>
                                <Text size="sm" c="dimmed">{reviewData.courseDescription}</Text>
                                <Text size="sm" c="dimmed">Course ID: {reviewData.courseId}</Text>
                                {reviewData.draft && (
                                    <Text size="sm" c="dimmed">
                                        Cập nhật lần cuối: {new Date(reviewData.draft.updated_at).toLocaleString('vi-VN')}
                                    </Text>
                                )}
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
                                    <Button
                                        variant="outline"
                                        leftSection={<IconMessageCircle size={16} />}
                                        onClick={() => setShowChat(!showChat)}
                                    >
                                        {showChat ? 'Ẩn Chat' : 'Chat với AI'}
                                    </Button>
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

                            {!reviewData.draft ? (
                                <Paper withBorder p="xl" style={{ textAlign: 'center' }}>
                                    <Stack gap="md" align="center">
                                        <IconRobot size={48} style={{ color: 'var(--mantine-color-violet-6)' }} />
                                        <Text size="lg" fw={500}>Đang tạo nội dung khóa học...</Text>
                                        <Text size="sm" c="dimmed">
                                            AI Agent đang phân tích và tạo nội dung cho khóa học này.
                                            Vui lòng chờ trong giây lát hoặc chat với AI để theo dõi tiến trình.
                                        </Text>
                                    </Stack>
                                </Paper>
                            ) : (
                                <Stack gap="md">
                                    {(() => {
                                        let generatedContent;
                                        try {
                                            generatedContent = JSON.parse(reviewData.draft.agent_content);
                                        } catch (e) {
                                            console.error('Error parsing draft content:', e);
                                            return (
                                                <Alert icon={<IconAlertCircle size={16} />} title="Lỗi" color="red">
                                                    Không thể phân tích nội dung đã tạo
                                                </Alert>
                                            );
                                        }

                                        return (
                                            <>
                                                {/* Topics */}
                                                {generatedContent.topics && (
                                                    <Paper withBorder p="md">
                                                        <Title order={4} mb="sm">Topics ({generatedContent.topics.length})</Title>
                                                        <Stack gap="xs">
                                                            {generatedContent.topics.map((topic: any, index: number) => (
                                                                <Group key={topic.id || index} justify="space-between">
                                                                    <div>
                                                                        <Text fw={500}>{topic.name}</Text>
                                                                        <Text size="sm" c="dimmed">{topic.description}</Text>
                                                                    </div>
                                                                    {topic.duration && (
                                                                        <Text size="sm" c="dimmed">{topic.duration} phút</Text>
                                                                    )}
                                                                </Group>
                                                            ))}
                                                        </Stack>
                                                    </Paper>
                                                )}

                                                {/* Lessons */}
                                                {generatedContent.lessons && (
                                                    <Paper withBorder p="md">
                                                        <Title order={4} mb="sm">Bài học ({generatedContent.lessons.length})</Title>
                                                        <Stack gap="xs">
                                                            {generatedContent.lessons.map((lesson: any, index: number) => (
                                                                <Group key={lesson.id || index} justify="space-between">
                                                                    <Text>{lesson.name}</Text>
                                                                    {lesson.duration && (
                                                                        <Text size="sm" c="dimmed">{lesson.duration} phút</Text>
                                                                    )}
                                                                </Group>
                                                            ))}
                                                        </Stack>
                                                    </Paper>
                                                )}

                                                {/* Exercises */}
                                                {generatedContent.exercises && (
                                                    <Paper withBorder p="md">
                                                        <Title order={4} mb="sm">Bài tập ({generatedContent.exercises.length})</Title>
                                                        <Stack gap="xs">
                                                            {generatedContent.exercises.map((exercise: any, index: number) => (
                                                                <Group key={exercise.id || index} justify="space-between">
                                                                    <div>
                                                                        <Text>{exercise.name}</Text>
                                                                        <Text size="sm" c="dimmed">{exercise.description}</Text>
                                                                    </div>
                                                                    {exercise.difficulty && (
                                                                        <Badge size="sm" color={
                                                                            exercise.difficulty === 'Easy' ? 'green' :
                                                                                exercise.difficulty === 'Medium' ? 'yellow' : 'red'
                                                                        }>
                                                                            {exercise.difficulty}
                                                                        </Badge>
                                                                    )}
                                                                </Group>
                                                            ))}
                                                        </Stack>
                                                    </Paper>
                                                )}

                                                {/* Tests */}
                                                {generatedContent.tests && (
                                                    <Paper withBorder p="md">
                                                        <Title order={4} mb="sm">Bài kiểm tra ({generatedContent.tests.length})</Title>
                                                        <Stack gap="xs">
                                                            {generatedContent.tests.map((test: any, index: number) => (
                                                                <Group key={test.id || index} justify="space-between">
                                                                    <Text>{test.name}</Text>
                                                                    <Text size="sm" c="dimmed">
                                                                        {test.questions} câu hỏi - {test.duration} phút
                                                                    </Text>
                                                                </Group>
                                                            ))}
                                                        </Stack>
                                                    </Paper>
                                                )}
                                            </>
                                        );
                                    })()}
                                </Stack>
                            )}

                            <Divider />

                            {/* Action Buttons */}
                            {reviewData.draft && (
                                <Group justify="center">
                                    <Button
                                        color="red"
                                        variant="outline"
                                        leftSection={<IconX size={16} />}
                                        onClick={handleRejectContent}
                                        loading={approveRejectMutation.isPending}
                                    >
                                        Từ chối và yêu cầu tạo lại
                                    </Button>
                                    <Button
                                        color="green"
                                        leftSection={<IconCheck size={16} />}
                                        onClick={handleApproveContent}
                                        loading={approveRejectMutation.isPending}
                                    >
                                        Chấp nhận và lưu nội dung
                                    </Button>
                                </Group>
                            )}
                        </Card>
                    </Stack>
                </Grid.Col>

                {/* Right Column - Chat */}
                {showChat && (
                    <Grid.Col span={4}>
                        <Card withBorder shadow="sm" p="lg" style={{ height: '80vh', display: 'flex', flexDirection: 'column' }}>
                            <Group justify="space-between" mb="md">
                                <Title order={3}>Chat với AI Agent</Title>
                                <ActionIcon
                                    variant="subtle"
                                    color="gray"
                                    onClick={() => setShowChat(false)}
                                >
                                    <IconX size={16} />
                                </ActionIcon>
                            </Group>

                            <div style={{ flex: 1 }}>
                                <AdminChat />
                            </div>
                        </Card>
                    </Grid.Col>
                )}
            </Grid>
        </Container>
    );
}
