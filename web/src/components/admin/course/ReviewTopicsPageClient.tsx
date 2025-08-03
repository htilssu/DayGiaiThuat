"use client";

import {
    Container,
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
    Button,
    NumberInput,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState, useEffect } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { 
    GenerateTopicsRequest,
    GeneratedTopic,
    GenerateTopicsResponse,
    generateCourseTopics 
} from "@/lib/api/admin-courses";
import { adminTopicsApi, AdminTopicCreatePayload } from "@/lib/api/admin-topics";
import { notifications } from '@mantine/notifications';
import { IconCheck, IconAlertCircle, IconEdit, IconTrash, IconClock, IconTarget, IconBook, IconDeviceFloppy, IconRocket, IconArrowLeft } from "@tabler/icons-react";
import { useRouter } from "next/navigation";

interface CourseData {
    title: string;
    description: string;
    level: string;
    courseId: number;
    price: number;
    duration: number;
    isPublished: boolean;
    tags: string;
    requirements: string;
    whatYouWillLearn: string;
}

interface ReviewTopicsPageClientProps {
    courseId: string;
}

export default function ReviewTopicsPageClient({ courseId }: ReviewTopicsPageClientProps) {
    const [courseData, setCourseData] = useState<CourseData | null>(null);
    const [generatedTopics, setGeneratedTopics] = useState<GenerateTopicsResponse | null>(null);
    const [editingTopics, setEditingTopics] = useState<GeneratedTopic[]>([]);
    const [isGeneratingTopics, setIsGeneratingTopics] = useState(false);
    const [isSavingTopics, setIsSavingTopics] = useState(false);
    
    const queryClient = useQueryClient();
    const router = useRouter();

    const generateForm = useForm({
        initialValues: {
            maxTopics: 5,
        },
        validate: {
            maxTopics: (value) =>
                value < 3 || value > 10 ? "Số lượng topics phải từ 3-10" : null,
        },
    });

    // Load course data from sessionStorage
    useEffect(() => {
        const storedData = sessionStorage.getItem('pendingCourseData');
        if (storedData) {
            const data = JSON.parse(storedData) as CourseData;
            setCourseData(data);
            sessionStorage.removeItem('pendingCourseData');
        }
    }, []);

    // Mutation for generating topics
    const generateTopicsMutation = useMutation({
        mutationFn: async (data: GenerateTopicsRequest) => {
            setIsGeneratingTopics(true);
            return await generateCourseTopics(data);
        },
        onSuccess: (response) => {
            setGeneratedTopics(response);
            setEditingTopics([...response.topics]);
            notifications.show({
                title: 'Thành công',
                message: 'Topics đã được tạo thành công! Hãy xem lại trước khi lưu.',
                color: 'green',
            });
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.message || 'Không thể tạo topics. Vui lòng thử lại.',
                color: 'red',
            });
        },
        onSettled: () => {
            setIsGeneratingTopics(false);
        }
    });

    // Mutation for saving topics to database
    const saveTopicsMutation = useMutation({
        mutationFn: async (topics: GeneratedTopic[]) => {
            setIsSavingTopics(true);
            const promises = topics.map(async (topic, index) => {
                const topicData: AdminTopicCreatePayload = {
                    name: topic.name,
                    description: topic.description,
                    courseId: parseInt(courseId),
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
            queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
            notifications.show({
                title: 'Thành công',
                message: `Đã lưu ${createdTopics.length} topics thành công!`,
                color: 'green',
            });
            
            // Navigate back to course management
            router.push('/admin/course');
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.message || 'Không thể lưu topics. Vui lòng thử lại.',
                color: 'red',
            });
        },
        onSettled: () => {
            setIsSavingTopics(false);
        }
    });

    const handleGenerateTopics = async (values: typeof generateForm.values) => {
        if (!courseData) return;
        
        const request: GenerateTopicsRequest = {
            title: courseData.title,
            description: courseData.description,
            level: courseData.level,
            maxTopics: values.maxTopics,
        };
        
        generateTopicsMutation.mutate(request);
    };

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

    const handleBackToCourses = () => {
        router.push('/admin/course');
    };

    if (!courseData) {
        return (
            <Container size="lg" py="xl">
                <Alert icon={<IconAlertCircle size="1rem" />} title="Lỗi" color="red">
                    Không tìm thấy thông tin khóa học. Vui lòng tạo lại khóa học.
                </Alert>
            </Container>
        );
    }

    return (
        <Container size="xl" py="xl">
            <LoadingOverlay visible={isGeneratingTopics || isSavingTopics} />
            
            <Stack gap="xl">
                {/* Header */}
                <Group justify="space-between">
                    <div>
                        <Group gap="md" mb="sm">
                            <Button
                                variant="light"
                                leftSection={<IconArrowLeft size={16} />}
                                onClick={handleBackToCourses}
                            >
                                Quay lại
                            </Button>
                            <Badge variant="filled" color="blue">Course ID: {courseId}</Badge>
                        </Group>
                        <Title order={1} className="text-primary">
                            Review và Tạo Topics
                        </Title>
                        <Text size="lg" c="dimmed">
                            {courseData.title}
                        </Text>
                    </div>
                </Group>

                {/* Course Info */}
                <Paper p="lg" withBorder>
                    <Title order={3} mb="md" className="text-accent">
                        <IconBook size={20} style={{ marginRight: 8 }} />
                        Thông tin khóa học
                    </Title>
                    <Group gap="xl">
                        <div>
                            <Text size="sm" fw={500} c="dimmed">Tiêu đề:</Text>
                            <Text>{courseData.title}</Text>
                        </div>
                        <div>
                            <Text size="sm" fw={500} c="dimmed">Cấp độ:</Text>
                            <Badge variant="light" color="blue">{courseData.level}</Badge>
                        </div>
                        <div>
                            <Text size="sm" fw={500} c="dimmed">Giá:</Text>
                            <Text>{courseData.price === 0 ? 'Miễn phí' : `${courseData.price.toLocaleString()}₫`}</Text>
                        </div>
                    </Group>
                    <Text size="sm" mt="md" c="dimmed">
                        {courseData.description}
                    </Text>
                </Paper>

                {/* Generate Topics Section */}
                {!generatedTopics && (
                    <Paper p="lg" withBorder>
                        <Title order={3} mb="md" className="text-accent">
                            <IconRocket size={20} style={{ marginRight: 8 }} />
                            Tạo Topics với AI
                        </Title>
                        
                        <form onSubmit={generateForm.onSubmit(handleGenerateTopics)}>
                            <Group gap="md" align="end">
                                <NumberInput
                                    label="Số lượng topics tối đa"
                                    placeholder="5"
                                    min={3}
                                    max={10}
                                    style={{ width: 200 }}
                                    {...generateForm.getInputProps("maxTopics")}
                                />
                                <Button
                                    type="submit"
                                    leftSection={<IconTarget size={16} />}
                                    loading={isGeneratingTopics}
                                >
                                    Tạo Topics với AI
                                </Button>
                            </Group>
                        </form>
                    </Paper>
                )}

                {/* Generated Topics Section */}
                {generatedTopics && (
                    <Paper p="lg" withBorder>
                        <Group justify="space-between" mb="lg">
                            <div>
                                <Title order={3} className="text-primary">
                                    {editingTopics.length} Topics được tạo
                                </Title>
                                <Group gap="xs" mt="xs">
                                    <IconClock size={16} />
                                    <Text size="sm" c="dimmed">
                                        Ước tính thời gian: {generatedTopics.duration}
                                    </Text>
                                </Group>
                            </div>
                            <Badge variant="light" color="green" size="lg">
                                {generatedTopics.status}
                            </Badge>
                        </Group>

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
                                        
                                        {/* Add skill input */}
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
                                onClick={() => {
                                    setGeneratedTopics(null);
                                    setEditingTopics([]);
                                }}
                                leftSection={<IconEdit size={16} />}
                            >
                                Tạo lại Topics
                            </Button>
                            <Button
                                onClick={handleSaveTopics}
                                leftSection={<IconDeviceFloppy size={16} />}
                                loading={isSavingTopics}
                                color="green"
                                disabled={editingTopics.length === 0}
                            >
                                Lưu {editingTopics.length} Topics vào Khóa học
                            </Button>
                        </Group>
                    </Paper>
                )}
            </Stack>
        </Container>
    );
}
