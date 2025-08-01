"use client";

import React from "react";
import { Card, Group, Text, RingProgress, Badge, Stack } from "@mantine/core";
import { IconLock } from "@tabler/icons-react";
import { UITopic, topicsData } from "./topicsData";

interface TopicCardProps {
    topic: UITopic;
    index: number;
    isExpanded: boolean;
    toggleExpand: () => void;
}

export function TopicCard({ topic, index, isExpanded, toggleExpand }: TopicCardProps) {
    const getColorByTopic = (color: string) => {
        const colorMap: { [key: string]: string } = {
            primary: "blue",
            secondary: "green",
            accent: "orange",
            warning: "yellow",
            success: "teal",
            error: "red"
        };
        return colorMap[color] || "blue";
    };

    return (
        <Card
            shadow="sm"
            padding="lg"
            radius="md"
            withBorder
            style={{
                opacity: topic.isLocked ? 0.6 : 1,
                cursor: topic.isLocked ? "not-allowed" : "pointer",
                transition: "all 0.3s ease"
            }}
            onClick={!topic.isLocked ? toggleExpand : undefined}
        >
            <Group justify="space-between" mb="xs">
                <Group>
                    <Text size="xl">{topic.icon}</Text>
                    <div>
                        <Text fw={500} size="lg">
                            {topic.title}
                        </Text>
                        <Text size="sm" c="dimmed">
                            {topic.description}
                        </Text>
                    </div>
                    {topic.isLocked && <IconLock size={20} color="gray" />}
                </Group>
                <RingProgress
                    size={60}
                    thickness={8}
                    sections={[
                        { value: topic.progress, color: getColorByTopic(topic.color) }
                    ]}
                    label={
                        <Text size="xs" ta="center" fw={700}>
                            {topic.progress}%
                        </Text>
                    }
                />
            </Group>

            <Group justify="space-between" mt="md">
                <Badge color={getColorByTopic(topic.color)} variant="light">
                    {topic.completedLessons}/{topic.totalLessons} bài học
                </Badge>
                <Text size="sm" c="dimmed">
                    Chủ đề {index + 1}
                </Text>
            </Group>

            {isExpanded && topic.lessons && (
                <Stack gap="xs" mt="md">
                    <Text size="sm" fw={500}>
                        Danh sách bài học:
                    </Text>
                    {topic.lessons.map((lesson, lessonIndex) => (
                        <Group key={lesson.id} justify="space-between">
                            <Text
                                size="sm"
                                style={{
                                    textDecoration: lesson.isCompleted ? "line-through" : "none",
                                    opacity: lesson.isCompleted ? 0.7 : 1
                                }}
                            >
                                {lessonIndex + 1}. {lesson.title}
                            </Text>
                            <Badge
                                size="xs"
                                color={lesson.isCompleted ? "green" : "gray"}
                                variant={lesson.isCompleted ? "filled" : "outline"}
                            >
                                {lesson.isCompleted ? "Hoàn thành" : "Chưa học"}
                            </Badge>
                        </Group>
                    ))}
                </Stack>
            )}
        </Card>
    );
} 