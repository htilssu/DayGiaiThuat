"use client";

import { useEffect, useState } from "react";
import { getCourseById } from "@/lib/api/courses";
import { getTopicsWithLessons, Topic, Lesson } from "@/lib/api/topics";
import Link from "next/link";
import { Container, Title, Text, Card, Group, Button, Loader, Alert, List, ThemeIcon, Paper, Grid, Divider, Badge } from "@mantine/core";
import { IconAlertCircle, IconCircleCheck, IconCircleDashed, IconBook } from "@tabler/icons-react";

interface TopicWithLessons extends Topic {
    lessons: Lesson[];
    progress: number;
    lessonsCount: number;
}

interface CourseLearnClientProps {
    courseId: number;
}

export default function CourseLearnClient({ courseId }: CourseLearnClientProps) {
    const [course, setCourse] = useState<any>(null);
    const [topics, setTopics] = useState<TopicWithLessons[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchCourseData = async () => {
            try {
                // Lấy thông tin khóa học
                const courseData = await getCourseById(courseId);
                setCourse(courseData);

                // Lấy topics và lessons từ API
                const topicsData = await getTopicsWithLessons(courseId);

                // Tính toán progress và lessons count cho mỗi topic
                const enrichedTopics: TopicWithLessons[] = topicsData.map((topic) => {
                    const completedLessons = topic.lessons.filter(lesson => lesson.is_completed).length;
                    const totalLessons = topic.lessons.length;
                    const progress = totalLessons > 0 ? Math.round((completedLessons / totalLessons) * 100) : 0;

                    return {
                        ...topic,
                        progress,
                        lessonsCount: totalLessons
                    };
                });

                setTopics(enrichedTopics);
            } catch (err) {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError("Đã xảy ra lỗi khi tải dữ liệu khóa học.");
                }
            } finally {
                setLoading(false);
            }
        };

        fetchCourseData();
    }, [courseId]);

    if (loading) {
        return (
            <Container size="lg" py="xl" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '70vh' }}>
                <Loader size="xl" />
            </Container>
        );
    }

    if (error) {
        return (
            <Container size="lg" py="xl">
                <Alert icon={<IconAlertCircle size="1rem" />} title="Lỗi" color="red">
                    {error}
                </Alert>
            </Container>
        );
    }

    return (
        <Container size="lg" py="xl">
            <Title order={1} mb="md">
                {course.title}
            </Title>
            <Text mb="xl" size="lg">
                {course.description}
            </Text>

            <Divider mb="xl" />

            <Title order={2} mb="lg">
                Lộ trình học tập
            </Title>

            {topics.length === 0 ? (
                <Text ta="center" size="lg" color="dimmed">
                    Khóa học này chưa có chủ đề nào.
                </Text>
            ) : (
                <Grid>
                    {topics.map((topic) => (
                        <Grid.Col key={topic.id} span={12}>
                            <Paper shadow="xs" p="md" mb="md" withBorder>
                                <Group justify="space-between" mb="md">
                                    <div>
                                        <Title order={3}>{topic.name}</Title>
                                        <Text size="sm" c="dimmed">
                                            {topic.lessonsCount} bài học
                                        </Text>
                                    </div>
                                    <Badge color="blue" size="lg">
                                        {topic.progress}% hoàn thành
                                    </Badge>
                                </Group>

                                <Text mb="md">{topic.description}</Text>

                                <List spacing="xs" size="sm" mb="md" center>
                                    {topic.lessons && topic.lessons.map((lesson) => (
                                        <List.Item
                                            key={lesson.id}
                                            icon={
                                                <ThemeIcon color={lesson.is_completed ? "green" : "gray"} size={24} radius="xl">
                                                    {lesson.is_completed ? <IconCircleCheck size={16} /> : <IconCircleDashed size={16} />}
                                                </ThemeIcon>
                                            }
                                        >
                                            <Link href={`/topics/${topic.id}/lessons/${lesson.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                                                <Text size="md">{lesson.title}</Text>
                                            </Link>
                                        </List.Item>
                                    ))}
                                </List>

                                <Link href={`/topics/${topic.id}`} passHref>
                                    <Button
                                        leftSection={<IconBook size={16} />}
                                        variant="light"
                                        color="blue"
                                        component="a"
                                    >
                                        Xem chủ đề
                                    </Button>
                                </Link>
                            </Paper>
                        </Grid.Col>
                    ))}
                </Grid>
            )}
        </Container>
    );
} 