"use client";

import {
    Button,
    Modal,
    Title,
    Paper,
    Group,
    LoadingOverlay,
    Alert,
    Text,
    Card,
    Badge,
    List,
    ThemeIcon,
    Stack,
    Box,
    ActionIcon,
    Tooltip,
    TextInput,
    Textarea,
} from "@mantine/core";
import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { 
    GeneratedTopic,
    GenerateTopicsResponse 
} from "@/lib/api/admin-courses";
import { adminTopicsApi, AdminTopicCreatePayload } from "@/lib/api/admin-topics";
import { notifications } from '@mantine/notifications';
import { IconCheck, IconAlertCircle, IconEdit, IconTrash, IconClock, IconTarget, IconBook, IconDeviceFloppy } from "@tabler/icons-react";

interface SaveTopicsModalProps {
    opened: boolean;
    onClose: () => void;
    topicsData: GenerateTopicsResponse | null;
    courseId: number;
    onSuccess: () => void;
}

export default function SaveTopicsModal({ opened, onClose, topicsData, courseId, onSuccess }: SaveTopicsModalProps) {
    const [editingTopics, setEditingTopics] = useState<GeneratedTopic[]>([]);
    const [isSaving, setIsSaving] = useState(false);
    
    const queryClient = useQueryClient();

    // Initialize editing topics when modal opens
    useEffect(() => {
        if (topicsData && opened) {
            setEditingTopics([...topicsData.topics]);
        }
    }, [topicsData, opened]);

    // Mutation for saving topics to database
    const saveTopicsMutation = useMutation({
        mutationFn: async (topics: GeneratedTopic[]) => {
            setIsSaving(true);
            const promises = topics.map(async (topic, index) => {
                const topicData: AdminTopicCreatePayload = {
                    name: topic.name,
                    description: topic.description,
                    courseId: courseId,
                };
                
                // Create topic first
                const createdTopic = await adminTopicsApi.createTopicAdmin(topicData);
                
                // TODO: Create skills for this topic
                // This would require a new API endpoint for creating skills
                console.log(`Topic ${createdTopic.id} created with skills:`, topic.skills);
                
                return createdTopic;
            });
            
            return Promise.all(promises);
        },
        onSuccess: (createdTopics) => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'topics'] });
            notifications.show({
                title: 'Thành công',
                message: `Đã lưu ${createdTopics.length} topics thành công!`,
                color: 'green',
            });
            onSuccess();
            onClose();
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.message || 'Không thể lưu topics. Vui lòng thử lại.',
                color: 'red',
            });
        },
        onSettled: () => {
            setIsSaving(false);
        }
    });

    const handleSaveTopics = () => {
        saveTopicsMutation.mutate(editingTopics);
    };

    const handleEditTopic = (index: number, field: keyof GeneratedTopic, value: any) => {
        const updatedTopics = [...editingTopics];
        updatedTopics[index] = {
            ...updatedTopics[index],
            [field]: value
        };
        setEditingTopics(updatedTopics);
    };

    const handleRemoveTopic = (index: number) => {
        const updatedTopics = editingTopics.filter((_, i) => i !== index);
        setEditingTopics(updatedTopics);
    };

    const handleRemoveSkill = (topicIndex: number, skillIndex: number) => {
        const updatedTopics = [...editingTopics];
        updatedTopics[topicIndex].skills.splice(skillIndex, 1);
        setEditingTopics(updatedTopics);
    };

    const handleAddSkill = (topicIndex: number, skill: string) => {
        if (!skill.trim()) return;
        
        const updatedTopics = [...editingTopics];
        updatedTopics[topicIndex].skills.push(skill.trim());
        setEditingTopics(updatedTopics);
    };

    if (!topicsData) {
        return null;
    }

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            title="Lưu Topics vào Khóa học"
            size="xl"
            closeOnClickOutside={false}
        >
            <LoadingOverlay visible={isSaving} />
            
            <Stack gap="lg">
                <Alert 
                    icon={<IconBook size="1rem" />} 
                    title="Xác nhận lưu Topics"
                    color="blue"
                >
                    <Text size="sm">
                        Bạn đang chuẩn bị lưu <strong>{editingTopics.length} topics</strong> vào khóa học. 
                        Có thể chỉnh sửa trước khi lưu.
                    </Text>
                    <Group gap="xs" mt="xs">
                        <IconClock size={16} />
                        <Text size="sm" c="dimmed">
                            Ước tính thời gian: {topicsData.duration}
                        </Text>
                    </Group>
                </Alert>

                <Stack gap="md">
                    {editingTopics.map((topic, index) => (
                        <Card key={index} withBorder shadow="sm" p="lg">
                            <Group justify="space-between" mb="md">
                                <Badge variant="filled" color="blue">
                                    Topic #{topic.order}
                                </Badge>
                                <ActionIcon
                                    color="red"
                                    variant="light"
                                    onClick={() => handleRemoveTopic(index)}
                                    disabled={editingTopics.length <= 1}
                                >
                                    <IconTrash size={16} />
                                </ActionIcon>
                            </Group>

                            <TextInput
                                label="Tên topic"
                                value={topic.name}
                                onChange={(e) => handleEditTopic(index, 'name', e.target.value)}
                                mb="md"
                                leftSection={<IconTarget size={16} />}
                            />

                            <Textarea
                                label="Mô tả"
                                value={topic.description}
                                onChange={(e) => handleEditTopic(index, 'description', e.target.value)}
                                rows={3}
                                mb="md"
                            />

                            {topic.prerequisites.length > 0 && (
                                <Box mb="md">
                                    <Text fw={500} size="sm" mb="xs" className="text-orange-600">
                                        Yêu cầu tiên quyết:
                                    </Text>
                                    <List size="sm" spacing="xs">
                                        {topic.prerequisites.map((prereq, prereqIndex) => (
                                            <List.Item key={prereqIndex} icon={
                                                <ThemeIcon size={16} radius="xl" color="orange">
                                                    <IconAlertCircle size={12} />
                                                </ThemeIcon>
                                            }>
                                                {prereq}
                                            </List.Item>
                                        ))}
                                    </List>
                                </Box>
                            )}

                            <Box>
                                <Text fw={500} size="sm" mb="xs" className="text-primary">
                                    Kỹ năng sẽ đạt được ({topic.skills.length} kỹ năng):
                                </Text>
                                <List size="sm" spacing="xs">
                                    {topic.skills.map((skill, skillIndex) => (
                                        <List.Item key={skillIndex} icon={
                                            <ThemeIcon size={16} radius="xl" color="green">
                                                <IconCheck size={12} />
                                            </ThemeIcon>
                                        }>
                                            <Group justify="space-between">
                                                <Text>{skill}</Text>
                                                <ActionIcon
                                                    size="xs"
                                                    color="red"
                                                    variant="subtle"
                                                    onClick={() => handleRemoveSkill(index, skillIndex)}
                                                >
                                                    <IconTrash size={10} />
                                                </ActionIcon>
                                            </Group>
                                        </List.Item>
                                    ))}
                                </List>
                                
                                {/* Simple add skill input */}
                                <TextInput
                                    placeholder="Thêm kỹ năng mới..."
                                    size="sm"
                                    mt="xs"
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter') {
                                            const input = e.target as HTMLInputElement;
                                            handleAddSkill(index, input.value);
                                            input.value = '';
                                        }
                                    }}
                                    rightSection={
                                        <Text size="xs" c="dimmed">
                                            Enter
                                        </Text>
                                    }
                                />
                            </Box>
                        </Card>
                    ))}
                </Stack>

                <Group justify="space-between" mt="xl">
                    <Button 
                        variant="outline" 
                        onClick={onClose}
                        disabled={isSaving}
                    >
                        Hủy
                    </Button>
                    <Button
                        onClick={handleSaveTopics}
                        leftSection={<IconDeviceFloppy size={16} />}
                        loading={isSaving}
                        color="green"
                        disabled={editingTopics.length === 0}
                    >
                        Lưu {editingTopics.length} Topics vào Khóa học
                    </Button>
                </Group>
            </Stack>
        </Modal>
    );
}
