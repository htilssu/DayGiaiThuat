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
    Paper,
    ActionIcon,
    Tooltip,
    Modal,
    Textarea,
    Stepper,
    Progress,
} from "@mantine/core";
import { useState, useEffect } from "react";
import {
    IconCheck,
    IconX,
    IconRefresh,
    IconAlertCircle,
    IconRobot,
    IconArrowRight,
    IconList,
    IconBook,
    IconTestPipe
} from "@tabler/icons-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notifications } from '@mantine/notifications';
import { useRouter } from "next/navigation";
import {
    DndContext,
    closestCenter,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
    DragEndEvent,
} from '@dnd-kit/core';
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import {
    useSortable,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

import {
    getCourseTopicsReview,
    reorderTopics,
    approveTopicsAndNext,
    rejectTopicsAndRegenerate,
    updateTopic
} from "@/lib/api/course-topics-review";
import { CourseTopicsReview, TopicReview } from "@/types/course-review";
import TopicCard from "./TopicCard";

interface SortableTopicProps {
    topic: TopicReview;
    courseId: number;
    index: number;
    onTopicUpdate: (updatedTopicsOrTopic: TopicReview[] | TopicReview) => void;
}

function SortableTopic({ topic, courseId, index, onTopicUpdate }: SortableTopicProps) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id: topic.id });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
    };

    return (
        <div ref={setNodeRef} style={style}>
            <TopicCard
                topic={topic}
                courseId={courseId}
                index={index}
                onTopicUpdate={onTopicUpdate}
                isDragging={isDragging}
                dragHandleProps={{ ...attributes, ...listeners }}
            />
        </div>
    );
}

interface CourseTopicsReviewPageClientProps {
    courseId: string;
}

export default function CourseTopicsReviewPageClient({ courseId }: CourseTopicsReviewPageClientProps) {
    const [showRejectModal, setShowRejectModal] = useState(false);
    const [rejectFeedback, setRejectFeedback] = useState('');
    const [localTopics, setLocalTopics] = useState<TopicReview[]>([]);
    const router = useRouter();
    const queryClient = useQueryClient();

    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        })
    );

    // Fetch course topics review data
    const { data: reviewData, isLoading, error, refetch } = useQuery<CourseTopicsReview>({
        queryKey: ['courseTopicsReview', courseId],
        queryFn: () => getCourseTopicsReview(parseInt(courseId)),
        retry: 1,
    });

    // Update local topics when data changes
    useEffect(() => {
        if (reviewData?.topics) {
            setLocalTopics([...reviewData.topics].sort((a, b) => a.order - b.order));
        }
    }, [reviewData]);

    // Reorder topics mutation
    const reorderMutation = useMutation({
        mutationFn: (reorderedTopics: TopicReview[]) =>
            updateTopic(parseInt(courseId), { topics: reorderedTopics }),
        onSuccess: (data) => {
            notifications.show({
                title: 'Thành công',
                message: data.message || 'Đã cập nhật topic thành công',
                color: 'green',
            });
            queryClient.invalidateQueries({ queryKey: ['courseTopicsReview', courseId] });
        },
        onError: (error: any) => {
            notifications.show({
                title: 'Lỗi',
                message: error.message || 'Có lỗi khi cập nhật thứ tự',
                color: 'red',
            });
            // Revert local state
            if (reviewData?.topics) {
                setLocalTopics([...reviewData.topics].sort((a, b) => a.order - b.order));
            }
        },
    });

    // Approve topics mutation
    const approveMutation = useMutation({
        mutationFn: () => approveTopicsAndNext(parseInt(courseId)),
        onSuccess: (data) => {
            notifications.show({
                title: 'Thành công',
                message: data.message || 'Đã chấp nhận topics, chuyển sang tạo bài học',
                color: 'green',
            });
            // Redirect to lessons review page
            router.push(`/admin/course/${courseId}/review-lessons`);
        },
        onError: (error: any) => {
            notifications.show({
                title: 'Lỗi',
                message: error.message || 'Có lỗi xảy ra',
                color: 'red',
            });
        },
    });

    // Update topic mutation (gửi toàn bộ topics)
    const updateTopicMutation = useMutation({
        mutationFn: (topics: TopicReview[]) =>
            reorderTopics(parseInt(courseId), { topics }),
        onSuccess: (data: any) => {
            notifications.show({
                title: 'Thành công',
                message: data.message || 'Đã cập nhật topic thành công',
                color: 'green',
            });
            queryClient.invalidateQueries({ queryKey: ['courseTopicsReview', courseId] });
        },
        onError: (error: any) => {
            notifications.show({
                title: 'Lỗi',
                message: error.message || 'Có lỗi khi cập nhật topic',
                color: 'red',
            });
            // Revert local state
            if (reviewData?.topics) {
                setLocalTopics([...reviewData.topics].sort((a, b) => a.order - b.order));
            }
        },
    });

    // Reject topics mutation  
    const rejectMutation = useMutation({
        mutationFn: (feedback: string) => rejectTopicsAndRegenerate(parseInt(courseId), feedback),
        onSuccess: (data) => {
            notifications.show({
                title: 'Đã gửi yêu cầu',
                message: data.message || 'Đã gửi yêu cầu tạo lại topics với feedback',
                color: 'orange',
            });
            setShowRejectModal(false);
            setRejectFeedback('');
            refetch();
        },
        onError: (error: any) => {
            notifications.show({
                title: 'Lỗi',
                message: error.message || 'Có lỗi xảy ra',
                color: 'red',
            });
            setShowRejectModal(false);
        },
    });

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event;

        if (over && active.id !== over.id) {
            const oldIndex = localTopics.findIndex((item) => item.id === active.id);
            const newIndex = localTopics.findIndex((item) => item.id === over.id);

            const newTopics = arrayMove(localTopics, oldIndex, newIndex);

            // Update order for all topics
            const reorderedTopics = newTopics.map((topic, index) => ({
                ...topic,
                order: index + 1
            }));

            setLocalTopics(reorderedTopics);

            // Use the common update function
            handleTopicUpdate(reorderedTopics);
        }
    };

    const handleTopicUpdate = (updatedTopicsOrTopic: TopicReview[] | TopicReview) => {
        let updatedTopics: TopicReview[];

        if (Array.isArray(updatedTopicsOrTopic)) {
            // For reorder - already have the complete list
            updatedTopics = updatedTopicsOrTopic;
            setLocalTopics(updatedTopics);
        } else {
            // For single topic update
            const updatedTopic = updatedTopicsOrTopic;
            updatedTopics = localTopics.map(topic =>
                topic.id === updatedTopic.id ? updatedTopic : topic
            );
            setLocalTopics(updatedTopics);
        }

        // Send complete topics data to server
        reorderMutation.mutate(updatedTopics);
    };

    const handleApproveTopics = () => {
        approveMutation.mutate();
    };

    const handleRejectTopics = () => {
        setShowRejectModal(true);
    };

    const handleConfirmReject = () => {
        if (!rejectFeedback.trim()) {
            notifications.show({
                title: 'Lỗi',
                message: 'Vui lòng nhập lý do từ chối',
                color: 'red',
            });
            return;
        }

        rejectMutation.mutate(rejectFeedback.trim());
    };

    if (isLoading) {
        return (
            <Container size="xl" py="xl">
                <LoadingOverlay visible />
                <Text ta="center" mt="xl">Đang tải thông tin review topics...</Text>
            </Container>
        );
    }

    if (error || !reviewData) {
        return (
            <Container size="xl" py="xl">
                <Alert icon={<IconAlertCircle size={16} />} title="Lỗi" color="red">
                    {error?.message || 'Không thể tải thông tin review topics'}
                </Alert>
            </Container>
        );
    }

    return (
        <Container size="xl" py="xl">
            <Stack gap="xl">
                {/* Header */}
                <Card withBorder shadow="sm" p="lg">
                    <Group justify="space-between" mb="md">
                        <Title order={2} c="blue">Review Topics - Bước 1</Title>
                        <Badge color="blue" size="lg" variant="light">
                            {localTopics.length} topics
                        </Badge>
                    </Group>

                    {/* Progress Steps */}
                    <Stepper active={0} mb="lg">
                        <Stepper.Step
                            icon={<IconList size={18} />}
                            label="Review Topics"
                            description="Kiểm tra và chỉnh sửa các chủ đề"
                        />
                        <Stepper.Step
                            icon={<IconBook size={18} />}
                            label="Review Lessons"
                            description="Tạo và kiểm tra bài học"
                        />
                        <Stepper.Step
                            icon={<IconTestPipe size={18} />}
                            label="Review Tests"
                            description="Tạo và kiểm tra bài kiểm tra"
                        />
                    </Stepper>

                    <Stack gap="sm">
                        <Text size="lg" fw={500}>Mô tả khóa học</Text>
                        <Text size="sm" c="dimmed">{reviewData.description}</Text>
                        <Text size="sm" c="dimmed">
                            <strong>Thời lượng ước tính:</strong> {reviewData.duration} giờ
                        </Text>
                        <Text size="sm" c="dimmed">
                            <strong>Session ID:</strong> {reviewData.sessionId}
                        </Text>
                    </Stack>
                </Card>

                {/* Topics List */}
                <Card withBorder shadow="sm" p="lg">
                    <Group justify="space-between" mb="md">
                        <Title order={3} c="violet">
                            <Group gap="xs">
                                <IconRobot size={20} />
                                Danh sách Topics
                            </Group>
                        </Title>
                        <Group>
                            <Tooltip label="Làm mới">
                                <ActionIcon
                                    variant="light"
                                    color="blue"
                                    onClick={() => refetch()}
                                    loading={isLoading}
                                >
                                    <IconRefresh size={16} />
                                </ActionIcon>
                            </Tooltip>
                        </Group>
                    </Group>

                    <Text size="sm" c="dimmed" mb="lg">
                        Kéo thả để thay đổi thứ tự các topics. Nhấn vào biểu tượng chỉnh sửa để cập nhật thông tin topic.
                    </Text>

                    {localTopics.length === 0 ? (
                        <Paper withBorder p="xl" style={{ textAlign: 'center' }}>
                            <Stack gap="md" align="center">
                                <IconRobot size={48} style={{ color: 'var(--mantine-color-violet-6)' }} />
                                <Text size="lg" fw={500}>Chưa có topics</Text>
                                <Text size="sm" c="dimmed">
                                    Các topics sẽ xuất hiện ở đây sau khi được tạo.
                                </Text>
                            </Stack>
                        </Paper>
                    ) : (
                        <DndContext
                            sensors={sensors}
                            collisionDetection={closestCenter}
                            onDragEnd={handleDragEnd}
                        >
                            <SortableContext
                                items={localTopics.map(topic => topic.id)}
                                strategy={verticalListSortingStrategy}
                            >
                                <Stack gap="md">
                                    {localTopics.map((topic, index) => (
                                        <SortableTopic
                                            key={topic.id}
                                            topic={topic}
                                            courseId={parseInt(courseId)}
                                            index={index}
                                            onTopicUpdate={handleTopicUpdate}
                                        />
                                    ))}
                                </Stack>
                            </SortableContext>
                        </DndContext>
                    )}
                </Card>

                {/* Action Buttons */}
                {localTopics.length > 0 && (
                    <Card withBorder shadow="sm" p="lg">
                        <Group justify="center" gap="md">
                            <Button
                                color="red"
                                variant="outline"
                                leftSection={<IconX size={16} />}
                                onClick={handleRejectTopics}
                                loading={rejectMutation.isPending}
                                disabled={approveMutation.isPending}
                            >
                                Từ chối và yêu cầu tạo lại
                            </Button>

                            <Button
                                color="green"
                                leftSection={<IconArrowRight size={16} />}
                                onClick={handleApproveTopics}
                                loading={approveMutation.isPending}
                                disabled={rejectMutation.isPending}
                            >
                                Chấp nhận và chuyển sang tạo Lessons
                            </Button>
                        </Group>
                    </Card>
                )}
            </Stack>

            {/* Reject Feedback Modal */}
            <Modal
                opened={showRejectModal}
                onClose={() => setShowRejectModal(false)}
                title="Từ chối topics và yêu cầu tạo lại"
                size="md"
                centered
            >
                <Stack gap="md">
                    <Text size="sm" c="dimmed">
                        Vui lòng nhập lý do từ chối và yêu cầu cụ thể để AI có thể tạo lại topics phù hợp hơn:
                    </Text>

                    <Textarea
                        label="Lý do từ chối và yêu cầu tạo lại"
                        placeholder="Ví dụ: Topics quá khó cho người mới bắt đầu, cần thêm topics cơ bản hơn, sắp xếp lại thứ tự từ dễ đến khó..."
                        value={rejectFeedback}
                        onChange={(event) => setRejectFeedback(event.currentTarget.value)}
                        minRows={4}
                        maxRows={8}
                        autosize
                        required
                    />

                    <Group justify="flex-end" gap="sm">
                        <Button
                            variant="outline"
                            onClick={() => {
                                setShowRejectModal(false);
                                setRejectFeedback('');
                            }}
                            disabled={rejectMutation.isPending}
                        >
                            Hủy
                        </Button>
                        <Button
                            color="red"
                            onClick={handleConfirmReject}
                            loading={rejectMutation.isPending}
                            leftSection={<IconX size={16} />}
                        >
                            Từ chối và gửi yêu cầu
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </Container>
    );
}
