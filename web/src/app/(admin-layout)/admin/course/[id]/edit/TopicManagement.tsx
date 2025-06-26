'use client';

import React, { useState } from 'react';
import { Button, TextInput, Checkbox, Modal, Group, Text, Box, Loader } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { getAllTopicsAdmin, assignTopicToCourseAdmin, type Topic } from '@/lib/api/admin-topics';

interface TopicManagementProps {
    courseId: number;
    opened: boolean;
    onClose: () => void;
}

export default function TopicManagement({ courseId, opened, onClose }: TopicManagementProps) {
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedTopics, setSelectedTopics] = useState<Set<number>>(new Set());
    const queryClient = useQueryClient();

    // Use useQuery to cache all topics
    const { data: topics = [], isLoading } = useQuery({
        queryKey: ['admin', 'topics', 'all'],
        queryFn: async () => {
            const response = await getAllTopicsAdmin();
            return response || [];
        },
        enabled: opened, // Only fetch when modal is opened
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    });

    // Update selected topics when topics data changes
    React.useEffect(() => {
        if (topics.length > 0 && courseId) {
            const courseTopics = topics.filter((topic: Topic) => topic.courseId === courseId);
            setSelectedTopics(new Set(courseTopics.map((topic: Topic) => topic.id)));
        }
    }, [topics, courseId]);

    const handleTopicToggle = async (topicId: number, isSelected: boolean) => {
        try {
            const topic = topics.find(t => t.id === topicId);
            if (!topic) return;

            // Assign or unassign topic to course
            await assignTopicToCourseAdmin(topicId, {
                courseId: isSelected ? courseId : null,
            });

            // Update local state
            const newSelectedTopics = new Set(selectedTopics);
            if (isSelected) {
                newSelectedTopics.add(topicId);
            } else {
                newSelectedTopics.delete(topicId);
            }
            setSelectedTopics(newSelectedTopics);

            // Invalidate and refetch topics to get latest data
            queryClient.invalidateQueries({ queryKey: ['admin', 'topics'] });

            notifications.show({
                title: 'Thành công',
                message: `Đã ${isSelected ? 'thêm' : 'xóa'} topic khỏi khóa học`,
                color: 'green',
            });
        } catch (error) {
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể cập nhật topic',
                color: 'red',
            });
        }
    };

    const filteredTopics = topics.filter(topic =>
        topic.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (topic.description && topic.description.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    return (
        <Modal
            opened={opened}
            onClose={onClose}
            title="Quản lý Topics cho Khóa học"
            size="lg"
        >
            <Box>
                <TextInput
                    placeholder="Tìm kiếm topic..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.currentTarget.value)}
                    mb="md"
                />

                {isLoading ? (
                    <Box style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
                        <Loader />
                    </Box>
                ) : (
                    <Box style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        {filteredTopics.map((topic) => (
                            <Box
                                key={topic.id}
                                style={{
                                    padding: '0.75rem',
                                    border: '1px solid #e9ecef',
                                    borderRadius: '0.375rem',
                                    marginBottom: '0.5rem',
                                }}
                            >
                                <Group justify="space-between" align="flex-start">
                                    <Box style={{ flex: 1 }}>
                                        <Text fw={500}>{topic.name}</Text>
                                        <Text size="sm" c="dimmed">
                                            {topic.description || 'Không có mô tả'}
                                        </Text>
                                    </Box>
                                    <Checkbox
                                        checked={selectedTopics.has(topic.id)}
                                        onChange={(e) => handleTopicToggle(topic.id, e.currentTarget.checked)}
                                    />
                                </Group>
                            </Box>
                        ))}

                        {filteredTopics.length === 0 && (
                            <Text ta="center" c="dimmed" py="xl">
                                Không tìm thấy topic nào
                            </Text>
                        )}
                    </Box>
                )}

                <Group justify="flex-end" mt="md">
                    <Button variant="outline" onClick={onClose}>
                        Đóng
                    </Button>
                </Group>
            </Box>
        </Modal>
    );
} 