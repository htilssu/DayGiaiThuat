"use client";

import {
    Card,
    Text,
    Badge,
    Group,
    Stack,
    ActionIcon,
    Collapse,
    Button,
    Modal,
    TextInput,
    Textarea,
    TagsInput,
    Paper,
    Divider,
    Tooltip,
} from "@mantine/core";
import {
    IconGripVertical,
    IconEdit,
    IconEye,
    IconEyeOff,
    IconCheck,
    IconX
} from "@tabler/icons-react";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { notifications } from "@mantine/notifications";
import { TopicReview, UpdateTopicRequest } from "@/types/course-review";
import { updateTopic } from "@/lib/api/course-topics-review";

interface TopicCardProps {
    topic: TopicReview;
    courseId: number;
    index: number;
    onTopicUpdate: (topicId: string, updatedTopic: Partial<TopicReview>) => void;
    isDragging?: boolean;
    dragHandleProps?: any;
}

export default function TopicCard({
    topic,
    courseId,
    index,
    onTopicUpdate,
    isDragging = false,
    dragHandleProps
}: TopicCardProps) {
    const [expanded, setExpanded] = useState(false);
    const [editModalOpen, setEditModalOpen] = useState(false);
    const [editForm, setEditForm] = useState<UpdateTopicRequest>({
        name: topic.name,
        description: topic.description,
        prerequisites: topic.prerequisites || [],
    });

    const updateTopicMutation = useMutation({
        mutationFn: (data: UpdateTopicRequest) => updateTopic(courseId, topic.id, data),
        onSuccess: (response) => {
            notifications.show({
                title: 'Thành công',
                message: response.message || 'Cập nhật topic thành công',
                color: 'green',
            });

            // Cập nhật local state
            onTopicUpdate(topic.id, {
                name: editForm.name,
                description: editForm.description,
                prerequisites: editForm.prerequisites,
            });

            setEditModalOpen(false);
        },
        onError: (error: any) => {
            notifications.show({
                title: 'Lỗi',
                message: error.message || 'Có lỗi xảy ra khi cập nhật topic',
                color: 'red',
            });
        },
    });

    const handleSaveEdit = () => {
        if (!editForm.name.trim()) {
            notifications.show({
                title: 'Lỗi',
                message: 'Tên topic không được để trống',
                color: 'red',
            });
            return;
        }

        updateTopicMutation.mutate(editForm);
    };

    const handleCancelEdit = () => {
        setEditForm({
            name: topic.name,
            description: topic.description,
            prerequisites: topic.prerequisites || [],
        });
        setEditModalOpen(false);
    };

    return (
        <>
            <Card
                withBorder
                shadow="sm"
                p="md"
                style={{
                    opacity: isDragging ? 0.5 : 1,
                    transform: isDragging ? 'rotate(5deg)' : 'none',
                    transition: 'all 0.2s ease'
                }}
            >
                <Group justify="space-between" align="flex-start" wrap="nowrap">
                    {/* Drag Handle */}
                    <div {...dragHandleProps}>
                        <ActionIcon
                            variant="transparent"
                            size="lg"
                            style={{ cursor: 'grab' }}
                        >
                            <IconGripVertical size={16} color="var(--mantine-color-gray-5)" />
                        </ActionIcon>
                    </div>

                    {/* Topic Content */}
                    <Stack gap="xs" style={{ flex: 1 }}>
                        <Group justify="space-between" align="flex-start">
                            <div style={{ flex: 1 }}>
                                <Group gap="xs" align="center" mb="xs">
                                    <Badge variant="light" color="blue" size="sm">
                                        Chủ đề {index + 1}
                                    </Badge>
                                    <Badge variant="light" color="violet" size="sm">
                                        {topic.skills?.length || 0} kỹ năng
                                    </Badge>
                                </Group>

                                <Text fw={600} size="md" lineClamp={2} mb="xs">
                                    {topic.name}
                                </Text>

                                <Text size="sm" c="dimmed" lineClamp={3}>
                                    {topic.description}
                                </Text>

                                {/* Prerequisites */}
                                {topic.prerequisites && topic.prerequisites.length > 0 && (
                                    <Group gap="xs" mt="xs">
                                        <Text size="xs" c="dimmed" fw={500}>Yêu cầu:</Text>
                                        {topic.prerequisites.map((prereq, idx) => (
                                            <Badge key={idx} variant="outline" size="xs" color="orange">
                                                {prereq}
                                            </Badge>
                                        ))}
                                    </Group>
                                )}
                            </div>

                            {/* Actions */}
                            <Group gap="xs">
                                <Tooltip label="Chỉnh sửa topic">
                                    <ActionIcon
                                        variant="light"
                                        color="blue"
                                        size="sm"
                                        onClick={() => setEditModalOpen(true)}
                                    >
                                        <IconEdit size={14} />
                                    </ActionIcon>
                                </Tooltip>

                                <Tooltip label={expanded ? "Thu gọn" : "Mở rộng"}>
                                    <ActionIcon
                                        variant="light"
                                        color="gray"
                                        size="sm"
                                        onClick={() => setExpanded(!expanded)}
                                    >
                                        {expanded ? <IconEyeOff size={14} /> : <IconEye size={14} />}
                                    </ActionIcon>
                                </Tooltip>
                            </Group>
                        </Group>

                        {/* Expanded Content */}
                        <Collapse in={expanded}>
                            <Divider mb="md" />

                            {/* Skills */}
                            {topic.skills && topic.skills.length > 0 && (
                                <Paper withBorder p="sm" mb="md">
                                    <Text fw={500} size="sm" mb="xs">Kỹ năng sẽ học được:</Text>
                                    <Stack gap="xs">
                                        {topic.skills.map((skill, skillIdx) => (
                                            <Group key={skill.id || skillIdx} align="flex-start" gap="sm">
                                                <Badge variant="dot" color="green" size="sm" />
                                                <div>
                                                    <Text fw={500} size="sm">{skill.name}</Text>
                                                    <Text size="xs" c="dimmed">{skill.description}</Text>
                                                </div>
                                            </Group>
                                        ))}
                                    </Stack>
                                </Paper>
                            )}

                            {/* Status */}
                            <Group gap="md">
                                <Group gap="xs">
                                    <Text size="xs" c="dimmed">Bài học:</Text>
                                    <Badge variant="light" color={topic.lessons?.length > 0 ? "green" : "gray"} size="xs">
                                        {topic.lessons?.length || 0}
                                    </Badge>
                                </Group>

                                <Group gap="xs">
                                    <Text size="xs" c="dimmed">Bài kiểm tra:</Text>
                                    <Badge variant="light" color={topic.tests?.length > 0 ? "green" : "gray"} size="xs">
                                        {topic.tests?.length || 0}
                                    </Badge>
                                </Group>
                            </Group>
                        </Collapse>
                    </Stack>
                </Group>
            </Card>

            {/* Edit Modal */}
            <Modal
                opened={editModalOpen}
                onClose={handleCancelEdit}
                title={`Chỉnh sửa Topic: ${topic.name}`}
                size="lg"
                centered
            >
                <Stack gap="md">
                    <TextInput
                        label="Tên topic"
                        placeholder="Nhập tên topic..."
                        value={editForm.name}
                        onChange={(event) =>
                            setEditForm(prev => ({ ...prev, name: event.currentTarget.value }))
                        }
                        required
                        error={!editForm.name.trim() ? "Tên topic không được để trống" : undefined}
                    />

                    <Textarea
                        label="Mô tả"
                        placeholder="Nhập mô tả chi tiết về topic..."
                        value={editForm.description}
                        onChange={(event) =>
                            setEditForm(prev => ({ ...prev, description: event.currentTarget.value }))
                        }
                        minRows={3}
                        maxRows={6}
                        autosize
                    />

                    <TagsInput
                        label="Yêu cầu tiên quyết"
                        placeholder="Nhập và nhấn Enter để thêm yêu cầu"
                        value={editForm.prerequisites}
                        onChange={(values) =>
                            setEditForm(prev => ({ ...prev, prerequisites: values }))
                        }
                        data={[]}
                        clearable
                    />

                    <Group justify="flex-end" gap="sm">
                        <Button
                            variant="outline"
                            onClick={handleCancelEdit}
                            disabled={updateTopicMutation.isPending}
                        >
                            Hủy
                        </Button>

                        <Button
                            onClick={handleSaveEdit}
                            loading={updateTopicMutation.isPending}
                            leftSection={<IconCheck size={16} />}
                        >
                            Lưu thay đổi
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </>
    );
}
