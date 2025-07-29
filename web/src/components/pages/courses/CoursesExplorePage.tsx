"use client";

import { useState, useEffect, Key } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAppSelector } from "@/lib/store";
import {
    Container,
    Title,
    Text,
    Grid,
    Card,
    Badge,
    Button,
    Loader,
    Alert,
    Group,
    Box,
    Divider,
    Pagination,
    TextInput,
    Select
} from "@mantine/core";
import { IconSearch, IconBook, IconClock, IconTrophy } from "@tabler/icons-react";
import { coursesApi, CourseListItem } from "@/lib/api/courses";

export function CoursesExplorePage() {
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [searchQuery, setSearchQuery] = useState<string>("");
    const [levelFilter, setLevelFilter] = useState<string | null>(null);
    const router = useRouter();
    const userState = useAppSelector((state) => state.user);

    const { data: courses, isLoading } = useQuery({
        queryKey: ['courses', currentPage],
        queryFn: async () => {
            const data = await coursesApi.getCourses(currentPage, 6);
            setTotalPages(data.totalPages);
            return data.items as CourseListItem[];
        },
        enabled: !!userState.user,
    });

    // Xử lý chuyển trang
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    // Chuyển đổi phút thành định dạng giờ:phút
    const formatDuration = (minutes: number) => {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours > 0 ? `${hours} giờ ` : ""}${mins > 0 ? `${mins} phút` : ""}`;
    };

    // Xử lý khi click vào course card - navigate tới trang chi tiết
    const handleCourseClick = (courseId: number) => {
        router.push(`/courses/${courseId}`);
    };

    const handleGoToMyCourses = () => {
        router.push('/courses');
    };

    return (
        <Container size="xl" py="xl">
            {/* Header Banner */}
            <Box mb="xl" p="xl" style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '16px',
                color: 'white',
                textAlign: 'center'
            }}>
                <Title order={1} mb="md" style={{ color: 'white' }}>
                    Khám phá khóa học
                </Title>
                <Text size="xl" mb="lg" style={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                    Tìm hiểu và đăng ký các khóa học về giải thuật và lập trình
                </Text>
                <Button
                    size="lg"
                    variant="white"
                    color="blue"
                    onClick={handleGoToMyCourses}
                >
                    Xem khóa học của tôi
                </Button>
            </Box>

            {/* Filter & Search */}
            <Box mb="xl">
                <Grid>
                    <Grid.Col span={{ base: 12, md: 8 }}>
                        <TextInput
                            placeholder="Tìm kiếm khóa học..."
                            leftSection={<IconSearch size={16} />}
                            value={searchQuery}
                            onChange={(event) => setSearchQuery(event.currentTarget.value)}
                            size="md"
                        />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, md: 4 }}>
                        <Select
                            placeholder="Chọn cấp độ"
                            data={[
                                { value: '', label: 'Tất cả cấp độ' },
                                { value: 'Beginner', label: 'Cơ bản' },
                                { value: 'Intermediate', label: 'Trung cấp' },
                                { value: 'Advanced', label: 'Nâng cao' }
                            ]}
                            value={levelFilter}
                            onChange={setLevelFilter}
                            clearable
                            size="md"
                        />
                    </Grid.Col>
                </Grid>
            </Box>

            <Divider mb="xl" />

            {/* Danh sách khóa học */}
            {isLoading ? (
                <Grid>
                    {[...Array(6)].map((_, i) => (
                        <Grid.Col key={i} span={{ base: 12, md: 6, lg: 4 }}>
                            <Card shadow="sm" padding="lg" radius="md" withBorder style={{ height: '400px' }}>
                                <Card.Section>
                                    <div style={{ height: 200, backgroundColor: '#f0f0f0' }} />
                                </Card.Section>
                                <Loader size="md" style={{ margin: '20px auto' }} />
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>
            ) : error ? (
                <Alert color="red" title="Lỗi">
                    {error}
                </Alert>
            ) : (
                <>
                    <Grid>
                        {courses?.map((course) => (
                            <Grid.Col key={course.id} span={{ base: 12, md: 6, lg: 4 }}>
                                <Card
                                    shadow="sm"
                                    padding="lg"
                                    radius="md"
                                    withBorder
                                    style={{ height: '100%', cursor: 'pointer', transition: 'transform 0.2s' }}
                                    onClick={() => handleCourseClick(course.id)}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.transform = 'translateY(-4px)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = 'translateY(0)';
                                    }}
                                >
                                    {/* Course Image */}
                                    <Card.Section>
                                        <div style={{
                                            height: 200,
                                            backgroundImage: course.thumbnailUrl
                                                ? `url(${course.thumbnailUrl})`
                                                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                            backgroundSize: 'cover',
                                            backgroundPosition: 'center',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}>
                                            {!course.thumbnailUrl && (
                                                <IconBook size={48} color="white" />
                                            )}
                                        </div>
                                    </Card.Section>

                                    <Box pt="md">
                                        {/* Course Title */}
                                        <Title order={4} lineClamp={2} mb="xs">
                                            {course.title}
                                        </Title>

                                        {/* Course Description */}
                                        <Text size="sm" c="dimmed" lineClamp={3} mb="md">
                                            {course.description}
                                        </Text>

                                        {/* Course Stats */}
                                        <Group gap="xs" mb="md">
                                            <Badge variant="light" color="green" leftSection={<IconClock size={12} />}>
                                                {formatDuration(course.duration)}
                                            </Badge>
                                            <Badge variant="light" color="orange" leftSection={<IconTrophy size={12} />}>
                                                {course.level}
                                            </Badge>
                                        </Group>

                                        {/* Price */}
                                        {course.price !== undefined && (
                                            <Group justify="space-between" mb="md">
                                                <Text size="lg" fw={700} c="blue">
                                                    {course.price === 0 ? 'Miễn phí' : `${course.price.toLocaleString()} VNĐ`}
                                                </Text>
                                            </Group>
                                        )}

                                        {/* Action Button */}
                                        <Button
                                            fullWidth
                                            variant="filled"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleCourseClick(course.id);
                                            }}
                                        >
                                            Xem chi tiết
                                        </Button>
                                    </Box>
                                </Card>
                            </Grid.Col>
                        ))}
                    </Grid>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <Box mt="xl" style={{ display: 'flex', justifyContent: 'center' }}>
                            <Pagination
                                total={totalPages}
                                value={currentPage}
                                onChange={handlePageChange}
                                size="lg"
                            />
                        </Box>
                    )}
                </>
            )}
        </Container>
    );
}
