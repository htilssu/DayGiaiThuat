"use client";

import { useEffect, useState } from "react";
import { getEnrolledCourses, EnrolledCourse } from "@/lib/api/courses";
import Link from "next/link";
import { Container, Title, Text, SimpleGrid, Card, Image, Badge, Group, Button, Loader, Alert, Progress } from "@mantine/core";
import { IconAlertCircle } from "@tabler/icons-react";

export default function LearnClient() {
    const [courses, setCourses] = useState<EnrolledCourse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchEnrolledCourses = async () => {
            try {
                const enrolledCourses = await getEnrolledCourses();
                setCourses(enrolledCourses);
            } catch (err) {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError("Đã xảy ra lỗi khi tải khóa học.");
                }
            } finally {
                setLoading(false);
            }
        };

        fetchEnrolledCourses();
    }, []);

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
            <Title order={1} mb="xl" ta="center">
                Tiếp tục học
            </Title>

            {courses.length === 0 ? (
                <Text ta="center" size="lg" color="dimmed">
                    Bạn chưa đăng ký khóa học nào.
                </Text>
            ) : (
                <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
                    {courses.map((course) => (
                        <Card shadow="sm" padding="lg" radius="md" withBorder key={course.id}>
                            <Card.Section>
                                <Image
                                    src={course.thumbnailUrl || "https://via.placeholder.com/300x150?text=No+Image"}
                                    height={160}
                                    alt={course.title}
                                />
                            </Card.Section>

                            <Group justify="space-between" mt="md" mb="xs">
                                <Text fw={500}>{course.title}</Text>
                                <Badge color="blue" variant="light">
                                    {course.status}
                                </Badge>
                            </Group>

                            <Text size="sm" c="dimmed" lineClamp={3} mb="md">
                                {course.description || "Không có mô tả."}
                            </Text>

                            <Progress value={course.progress} mb="md" color="blue" />
                            <Text size="xs" c="dimmed" mb="md">
                                Hoàn thành: {course.progress}%
                            </Text>

                            <Link href={`/courses/${course.id}/learn`} passHref>
                                <Button variant="light" color="blue" fullWidth mt="md" radius="md" component="a">
                                    Tiếp tục học
                                </Button>
                            </Link>
                        </Card>
                    ))}
                </SimpleGrid>
            )}
        </Container>
    );
} 