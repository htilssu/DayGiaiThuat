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

interface CourseReviewPageClientProps {
    courseId: string;
}

interface CourseData {
    title: string;
    description: string;
    level: string;
    price: number;
    duration: number;
    isPublished: boolean;
    tags: string;
    requirements: string;
    whatYouWillLearn: string;
    tempId?: string;
}

interface GeneratedContent {
    topics: any[];
    lessons: any[];
    exercises: any[];
    tests: any[];
    status: 'generating' | 'completed' | 'failed';
    progress: number;
}

export default function CourseReviewPageClient({ courseId }: CourseReviewPageClientProps) {
    const [courseData, setCourseData] = useState<CourseData | null>(null);
    const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [showChat, setShowChat] = useState(false);
    const router = useRouter();

    // Load course data from sessionStorage when component mounts
    useEffect(() => {
        const pendingData = sessionStorage.getItem('pendingCourseData');
        if (pendingData) {
            try {
                const data = JSON.parse(pendingData);
                setCourseData(data);
                // Start generating content automatically
                generateContent(data);
            } catch (error) {
                notifications.show({
                    title: 'Lỗi',
                    message: 'Không thể tải dữ liệu khóa học',
                    color: 'red',
                });
            }
        }
    }, []);

    const generateContent = async (data: CourseData) => {
        setIsGenerating(true);
        setGeneratedContent({
            topics: [],
            lessons: [],
            exercises: [],
            tests: [],
            status: 'generating',
            progress: 0
        });

        try {
            // Simulate AI content generation
            const steps = [
                { message: 'Đang phân tích nội dung khóa học...', progress: 20 },
                { message: 'Đang tạo topics...', progress: 40 },
                { message: 'Đang tạo bài học...', progress: 60 },
                { message: 'Đang tạo bài tập...', progress: 80 },
                { message: 'Hoàn thành!', progress: 100 }
            ];

            for (const step of steps) {
                await new Promise(resolve => setTimeout(resolve, 1500));
                setGeneratedContent(prev => prev ? {
                    ...prev,
                    progress: step.progress
                } : null);

                notifications.show({
                    title: 'AI đang làm việc',
                    message: step.message,
                    color: 'blue',
                    autoClose: 1000,
                });
            }

            // Mock generated content
            const mockContent = {
                topics: [
                    {
                        id: 1,
                        name: `Giới thiệu ${data.title}`,
                        description: `Tổng quan về ${data.title} và các khái niệm cơ bản`,
                        order: 1,
                        duration: 30
                    },
                    {
                        id: 2,
                        name: 'Thực hành cơ bản',
                        description: 'Các bài tập thực hành để làm quen',
                        order: 2,
                        duration: 45
                    },
                    {
                        id: 3,
                        name: 'Nâng cao và ứng dụng',
                        description: 'Các kỹ thuật nâng cao và ứng dụng thực tế',
                        order: 3,
                        duration: 60
                    }
                ],
                lessons: [
                    {
                        id: 1,
                        topicId: 1,
                        name: 'Bài 1: Khái niệm cơ bản',
                        content: 'Nội dung bài học về khái niệm cơ bản...',
                        duration: 15
                    },
                    {
                        id: 2,
                        topicId: 1,
                        name: 'Bài 2: Ví dụ minh họa',
                        content: 'Các ví dụ minh họa thực tế...',
                        duration: 15
                    }
                ],
                exercises: [
                    {
                        id: 1,
                        topicId: 1,
                        name: 'Bài tập 1: Cơ bản',
                        description: 'Bài tập về khái niệm cơ bản',
                        difficulty: 'Easy'
                    }
                ],
                tests: [
                    {
                        id: 1,
                        topicId: 1,
                        name: 'Kiểm tra cuối topic 1',
                        questions: 5,
                        duration: 10
                    }
                ],
                status: 'completed' as const,
                progress: 100
            };

            setGeneratedContent(mockContent);
        } catch (error) {
            setGeneratedContent(prev => prev ? {
                ...prev,
                status: 'failed'
            } : null);
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể tạo nội dung',
                color: 'red',
            });
        } finally {
            setIsGenerating(false);
        }
    };

    const handleApproveContent = async () => {
        try {
            notifications.show({
                title: 'Đang lưu nội dung',
                message: 'Nội dung đang được lưu vào khóa học...',
                color: 'blue',
            });

            // Here you would call API to save the generated content
            await new Promise(resolve => setTimeout(resolve, 2000));

            notifications.show({
                title: 'Thành công',
                message: 'Nội dung đã được lưu vào khóa học!',
                color: 'green',
            });

            // Clear sessionStorage and redirect
            sessionStorage.removeItem('pendingCourseData');
            router.push('/admin/course');
        } catch (error) {
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể lưu nội dung',
                color: 'red',
            });
        }
    };

    const handleRejectContent = () => {
        setGeneratedContent(null);
        setShowChat(true);
        notifications.show({
            title: 'Nội dung bị từ chối',
            message: 'Hãy chat với AI để yêu cầu tạo lại nội dung',
            color: 'orange',
        });
    };

    const handleRegenerateContent = () => {
        if (courseData) {
            generateContent(courseData);
        }
    };

    if (!courseData) {
        return (
            <Container size="xl" py="xl">
                <Alert icon={<IconAlertCircle size={16} />} title="Không có dữ liệu" color="red">
                    Không tìm thấy dữ liệu khóa học. Vui lòng quay lại trang tạo khóa học.
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
                                <Badge color="green" size="lg">Đã tạo</Badge>
                            </Group>

                            <Stack gap="sm">
                                <Group>
                                    <Text fw={500} w={120}>Tiêu đề:</Text>
                                    <Text>{courseData.title}</Text>
                                </Group>
                                <Group>
                                    <Text fw={500} w={120}>Cấp độ:</Text>
                                    <Badge variant="light">{courseData.level}</Badge>
                                </Group>
                                <Group>
                                    <Text fw={500} w={120}>Giá:</Text>
                                    <Text>{courseData.price.toLocaleString('vi-VN')} VNĐ</Text>
                                </Group>
                                <Group>
                                    <Text fw={500} w={120}>Thời lượng:</Text>
                                    <Text>{courseData.duration} phút</Text>
                                </Group>
                                <div>
                                    <Text fw={500} mb="xs">Mô tả:</Text>
                                    <Text c="dimmed">{courseData.description}</Text>
                                </div>
                            </Stack>
                        </Card>

                        {/* Generated Content */}
                        <Card withBorder shadow="sm" p="lg">
                            <Group justify="space-between" mb="md">
                                <Title order={2} c="violet">
                                    <Group gap="xs">
                                        <IconRobot size={24} />
                                        Nội dung do AI tạo
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
                                    {generatedContent?.status === 'completed' && (
                                        <Tooltip label="Tạo lại nội dung">
                                            <ActionIcon
                                                variant="light"
                                                color="blue"
                                                onClick={handleRegenerateContent}
                                            >
                                                <IconRefresh size={16} />
                                            </ActionIcon>
                                        </Tooltip>
                                    )}
                                </Group>
                            </Group>

                            <LoadingOverlay visible={isGenerating} />

                            {generatedContent?.status === 'generating' && (
                                <Alert icon={<IconRobot size={16} />} title="AI đang tạo nội dung" color="blue">
                                    <Text>Tiến độ: {generatedContent.progress}%</Text>
                                </Alert>
                            )}

                            {generatedContent?.status === 'completed' && (
                                <Stack gap="md">
                                    {/* Topics */}
                                    <Paper withBorder p="md">
                                        <Title order={4} mb="sm">Topics ({generatedContent.topics.length})</Title>
                                        <Stack gap="xs">
                                            {generatedContent.topics.map((topic) => (
                                                <Group key={topic.id} justify="space-between">
                                                    <div>
                                                        <Text fw={500}>{topic.name}</Text>
                                                        <Text size="sm" c="dimmed">{topic.description}</Text>
                                                    </div>
                                                    <Text size="sm" c="dimmed">{topic.duration} phút</Text>
                                                </Group>
                                            ))}
                                        </Stack>
                                    </Paper>

                                    {/* Lessons */}
                                    <Paper withBorder p="md">
                                        <Title order={4} mb="sm">Bài học ({generatedContent.lessons.length})</Title>
                                        <Stack gap="xs">
                                            {generatedContent.lessons.map((lesson) => (
                                                <Group key={lesson.id} justify="space-between">
                                                    <Text>{lesson.name}</Text>
                                                    <Text size="sm" c="dimmed">{lesson.duration} phút</Text>
                                                </Group>
                                            ))}
                                        </Stack>
                                    </Paper>

                                    {/* Exercises */}
                                    <Paper withBorder p="md">
                                        <Title order={4} mb="sm">Bài tập ({generatedContent.exercises.length})</Title>
                                        <Stack gap="xs">
                                            {generatedContent.exercises.map((exercise) => (
                                                <Group key={exercise.id} justify="space-between">
                                                    <div>
                                                        <Text>{exercise.name}</Text>
                                                        <Text size="sm" c="dimmed">{exercise.description}</Text>
                                                    </div>
                                                    <Badge size="sm" color={
                                                        exercise.difficulty === 'Easy' ? 'green' :
                                                        exercise.difficulty === 'Medium' ? 'yellow' : 'red'
                                                    }>
                                                        {exercise.difficulty}
                                                    </Badge>
                                                </Group>
                                            ))}
                                        </Stack>
                                    </Paper>

                                    {/* Tests */}
                                    <Paper withBorder p="md">
                                        <Title order={4} mb="sm">Bài kiểm tra ({generatedContent.tests.length})</Title>
                                        <Stack gap="xs">
                                            {generatedContent.tests.map((test) => (
                                                <Group key={test.id} justify="space-between">
                                                    <Text>{test.name}</Text>
                                                    <Text size="sm" c="dimmed">{test.questions} câu hỏi - {test.duration} phút</Text>
                                                </Group>
                                            ))}
                                        </Stack>
                                    </Paper>

                                    <Divider />

                                    {/* Action Buttons */}
                                    <Group justify="center">
                                        <Button
                                            color="red"
                                            variant="outline"
                                            leftSection={<IconX size={16} />}
                                            onClick={handleRejectContent}
                                        >
                                            Từ chối và yêu cầu tạo lại
                                        </Button>
                                        <Button
                                            color="green"
                                            leftSection={<IconCheck size={16} />}
                                            onClick={handleApproveContent}
                                        >
                                            Chấp nhận và lưu nội dung
                                        </Button>
                                    </Group>
                                </Stack>
                            )}

                            {generatedContent?.status === 'failed' && (
                                <Alert icon={<IconAlertCircle size={16} />} title="Lỗi tạo nội dung" color="red">
                                    <Group mt="md">
                                        <Button variant="outline" onClick={handleRegenerateContent}>
                                            Thử lại
                                        </Button>
                                        <Button variant="outline" onClick={() => setShowChat(true)}>
                                            Chat với AI để hỗ trợ
                                        </Button>
                                    </Group>
                                </Alert>
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
                                <AdminChat
                                    courseData={courseData}
                                    generatedContent={generatedContent}
                                    onContentUpdate={(newContent) => setGeneratedContent(newContent)}
                                />
                            </div>
                        </Card>
                    </Grid.Col>
                )}
            </Grid>
        </Container>
    );
}
