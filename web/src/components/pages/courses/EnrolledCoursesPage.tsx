"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
    Container,
    Title,
    Text,
    Grid,
    Card,
    Badge,
    Progress,
    Loader,
    Alert,
    Group,
    Box,
    Divider,
    Button
} from "@mantine/core";
import { IconAlertCircle, IconBook, IconClock, IconTrophy, IconArrowRight } from "@tabler/icons-react";
import { coursesApi, EnrolledCourse } from "@/lib/api/courses";

export function EnrolledCoursesPage() {
    const [courses, setCourses] = useState<EnrolledCourse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    useEffect(() => {
        const fetchEnrolledCourses = async () => {
            try {
                setLoading(true);
                const enrolledCourses = await coursesApi.getEnrolledCourses();
                setCourses(enrolledCourses);
            } catch (err) {
                if (err instanceof Error) {
                    setError(err.message);
                } else {
                    setError("Đã xảy ra lỗi khi tải khóa học đã đăng ký.");
                }
            } finally {
                setLoading(false);
            }
        };

        fetchEnrolledCourses();
    }, []);

    // Chuyển đổi phút thành định dạng giờ:phút
    const formatDuration = (minutes: number) => {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours > 0 ? `${hours} giờ ` : ""}${mins > 0 ? `${mins} phút` : ""}`;
    };

    const handleCourseClick = (courseId: number) => {
        router.push(`/courses/${courseId}`);
    };

    const handleLearnClick = (course: EnrolledCourse) => {
        if (course.currentLessonId) {
            // Nếu có bài học hiện tại, chuyển đến bài học đó
            router.push(`/lessons/${course.currentLessonId}`);
        } else {
            // Nếu không có bài học hiện tại, chuyển đến trang học tổng quát
            router.push(`/courses/${course.id}/learn`);
        }
    };

    const handleExploreMore = () => {
        router.push('/courses/explore');
    };

    if (loading) {
        return (
            <Container size="lg" py="xl">
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
                    <Loader size="xl" />
                </div>
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
            {/* Header */}
            <Box mb="xl">
                <Group justify="space-between" align="center" mb="md">
                    <Title order={1}>Khóa học của bạn</Title>
                    <Group gap="sm">
                        <Button
                            variant="light"
                            className="border-primary/20 text-primary hover:bg-primary/10"
                            rightSection={<IconTrophy size={16} />}
                            onClick={() => router.push('/tests')}
                        >
                            Kiểm tra
                        </Button>
                        <Button
                            variant="outline"
                            className="border-primary text-primary hover:bg-primary/10"
                            rightSection={<IconArrowRight size={16} />}
                            onClick={handleExploreMore}
                        >
                            Khám phá thêm
                        </Button>
                    </Group>
                </Group>
                <Text size="lg" c="dimmed">
                    Tiếp tục hành trình học tập của bạn
                </Text>
            </Box>

            <Divider mb="xl" />

            {courses.length === 0 ? (
                <Box ta="center" py="xl">
                    <Title order={3} mb="md" c="dimmed">
                        Bạn chưa đăng ký khóa học nào
                    </Title>
                    <Text size="lg" c="dimmed" mb="xl">
                        Hãy khám phá và đăng ký các khóa học thú vị để bắt đầu hành trình học tập
                    </Text>
                    <Button
                        size="lg"
                        style={{
                            backgroundColor: 'rgb(var(--color-primary))',
                            borderColor: 'rgb(var(--color-primary))',
                            color: 'white'
                        }}
                        onClick={handleExploreMore}
                    >
                        Khám phá khóa học
                    </Button>
                </Box>
            ) : (
                <Grid>
                    {courses.map((course) => (
                        <Grid.Col key={course.id} span={{ base: 12, md: 6, lg: 4 }}>
                            <Card
                                shadow="sm"
                                padding="lg"
                                radius="md"
                                withBorder
                                style={{ height: '100%', cursor: 'pointer' }}
                                onClick={() => handleCourseClick(course.id)}
                            >
                                {/* Course Image */}
                                {course.thumbnailUrl && (
                                    <Card.Section>
                                        <div style={{
                                            height: 200,
                                            backgroundImage: `url(${course.thumbnailUrl})`,
                                            backgroundSize: 'cover',
                                            backgroundPosition: 'center'
                                        }} />
                                    </Card.Section>
                                )}

                                <Box pt="md">
                                    {/* Course Title */}
                                    <Title order={4} lineClamp={2} mb="xs">
                                        {course.title}
                                    </Title>

                                    {/* Course Description */}
                                    <Text size="sm" c="dimmed" lineClamp={3} mb="md">
                                        {course.description}
                                    </Text>

                                    {/* Progress */}
                                    {course.progress !== undefined && (
                                        <Box mb="md">
                                            <Group justify="space-between" mb="xs">
                                                <Text size="sm" fw={500}>Tiến độ</Text>
                                                <Text size="sm">{Math.round(course.progress)}%</Text>
                                            </Group>
                                            <Progress value={course.progress} className="[&_.mantine-Progress-bar]:bg-primary" />
                                        </Box>
                                    )}

                                    {/* Course Stats */}
                                    <Group gap="xs" mb="md">
                                        <Badge variant="light" className="text-primary border-primary/20" leftSection={<IconBook size={12} />}>
                                            {course.topics?.length || 0} chủ đề
                                        </Badge>
                                        {course.duration && (
                                            <Badge variant="light" className="text-secondary border-secondary/20" leftSection={<IconClock size={12} />}>
                                                {formatDuration(course.duration)}
                                            </Badge>
                                        )}
                                        <Badge variant="light" className="text-accent border-accent/20" leftSection={<IconTrophy size={12} />}>
                                            {course.level}
                                        </Badge>
                                    </Group>

                                    {/* Action Button */}
                                    <Button
                                        fullWidth
                                        variant="filled"
                                        style={{
                                            backgroundColor: 'rgb(var(--color-primary))',
                                            borderColor: 'rgb(var(--color-primary))',
                                            color: 'white'
                                        }}
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleLearnClick(course);
                                        }}
                                    >
                                        Tiếp tục học
                                    </Button>
                                </Box>
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>
            )}
        </Container>
    );
}
