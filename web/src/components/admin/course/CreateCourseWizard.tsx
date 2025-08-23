"use client";

import {
    Button,
    Modal,
    TextInput,
    Textarea,
    Title,
    Paper,
    Group,
    Grid,
    NumberInput,
    Switch,
    LoadingOverlay,
    Alert,
    Text,
    Divider,
    Card,
    Badge,
    List,
    ThemeIcon,
    Container,
    Stepper,
    Stack,
    Box,
    ActionIcon,
    Tooltip,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useDisclosure } from "@mantine/hooks";
import { IconPlus, IconAlertCircle, IconCheck, IconEdit, IconTrash, IconClock, IconUsers, IconTarget, IconBook } from "@tabler/icons-react";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
    CourseCreatePayload,
    createCourseAdmin,
    generateCourseTopics,
    GenerateTopicsRequest,
    GeneratedTopic,
    GenerateTopicsResponse
} from "@/lib/api/admin-courses";
import { notifications } from '@mantine/notifications';
import SaveTopicsModal from './SaveTopicsModal';

interface CreateCourseWizardProps {
    opened: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export default function CreateCourseWizard({ opened, onClose, onSuccess }: CreateCourseWizardProps) {
    const [activeStep, setActiveStep] = useState(0);
    const [generatedTopics, setGeneratedTopics] = useState<GenerateTopicsResponse | null>(null);
    const [isGeneratingTopics, setIsGeneratingTopics] = useState(false);
    const [isCreatingCourse, setIsCreatingCourse] = useState(false);
    const [createdCourseId, setCreatedCourseId] = useState<number | null>(null);
    const [saveTopicsModalOpened, setSaveTopicsModalOpened] = useState(false);

    const queryClient = useQueryClient();

    const courseForm = useForm({
        initialValues: {
            title: "",
            description: "",
            level: "Beginner",
            price: 0,
            duration: 0,
            isPublished: false,
            tags: "",
            requirements: "",
            whatYouWillLearn: "",
            maxTopics: 5,
        },
        validate: {
            title: (value) =>
                value.length < 3 ? "Tiêu đề khóa học phải có ít nhất 3 ký tự" : null,
            description: (value) =>
                value.length < 10 ? "Mô tả khóa học phải có ít nhất 10 ký tự" : null,
            maxTopics: (value) =>
                value < 3 || value > 10 ? "Số lượng topics phải từ 3-10" : null,
        },
    });

    // Mutation for generating topics
    const generateTopicsMutation = useMutation({
        mutationFn: async (data: GenerateTopicsRequest) => {
            setIsGeneratingTopics(true);
            return await generateCourseTopics(data);
        },
        onSuccess: (response) => {
            setGeneratedTopics(response);
            setActiveStep(1); // Move to preview step
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

    // Mutation for creating course
    const createCourseMutation = useMutation({
        mutationFn: async (data: CourseCreatePayload) => {
            setIsCreatingCourse(true);
            return await createCourseAdmin(data);
        },
        onSuccess: (createdCourse) => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
            setCreatedCourseId(createdCourse.id);
            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được tạo thành công! Bây giờ hãy lưu topics.',
                color: 'green',
            });
            // Open save topics modal instead of closing immediately
            setSaveTopicsModalOpened(true);
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.message || 'Không thể tạo khóa học.',
                color: 'red',
            });
        },
        onSettled: () => {
            setIsCreatingCourse(false);
        }
    });

    const handleGenerateTopics = async (values: typeof courseForm.values) => {
        const request: GenerateTopicsRequest = {
            title: values.title,
            description: values.description,
            level: values.level,
            maxTopics: values.maxTopics,
        };

        generateTopicsMutation.mutate(request);
    };

    const handleCreateCourse = async () => {
        const values = courseForm.values;
        const courseData: CourseCreatePayload = {
            title: values.title,
            description: values.description,
            level: values.level,
            price: values.price,
            duration: values.duration,
            isPublished: values.isPublished,
            tags: values.tags,
            requirements: values.requirements,
            whatYouWillLearn: values.whatYouWillLearn,
        };

        createCourseMutation.mutate(courseData);
    };

    const handleClose = () => {
        setActiveStep(0);
        setGeneratedTopics(null);
        setCreatedCourseId(null);
        setSaveTopicsModalOpened(false);
        courseForm.reset();
        onClose();
    };

    const handleTopicsSaved = () => {
        setSaveTopicsModalOpened(false);
        handleClose();
        onSuccess();
    };

    const handleEditTopic = (index: number, field: keyof GeneratedTopic, value: any) => {
        if (!generatedTopics) return;

        const updatedTopics = [...generatedTopics.topics];
        updatedTopics[index] = {
            ...updatedTopics[index],
            [field]: value
        };

        setGeneratedTopics({
            ...generatedTopics,
            topics: updatedTopics
        });
    };

    const handleRemoveTopic = (index: number) => {
        if (!generatedTopics) return;

        const updatedTopics = generatedTopics.topics.filter((_, i) => i !== index);
        setGeneratedTopics({
            ...generatedTopics,
            topics: updatedTopics
        });
    };

    const handleAddSkill = (topicIndex: number, skill: string) => {
        if (!generatedTopics || !skill.trim()) return;

        const updatedTopics = [...generatedTopics.topics];
        updatedTopics[topicIndex].skills.push(skill.trim());

        setGeneratedTopics({
            ...generatedTopics,
            topics: updatedTopics
        });
    };

    const handleRemoveSkill = (topicIndex: number, skillIndex: number) => {
        if (!generatedTopics) return;

        const updatedTopics = [...generatedTopics.topics];
        updatedTopics[topicIndex].skills.splice(skillIndex, 1);

        setGeneratedTopics({
            ...generatedTopics,
            topics: updatedTopics
        });
    };

    return (
        <Modal
            opened={opened}
            onClose={handleClose}
            title="Tạo khóa học mới"
            size="xl"
            closeOnClickOutside={false}
        >
            <LoadingOverlay visible={isGeneratingTopics || isCreatingCourse} />

            <Stepper active={activeStep} onStepClick={setActiveStep} allowNextStepsSelect={false}>
                <Stepper.Step
                    label="Thông tin khóa học"
                    description="Nhập thông tin cơ bản"
                    icon={<IconBook size={18} />}
                >
                    <form onSubmit={courseForm.onSubmit(handleGenerateTopics)}>
                        <Stack gap="md">
                            <Grid>
                                <Grid.Col span={12}>
                                    <TextInput
                                        required
                                        label="Tiêu đề khóa học"
                                        placeholder="Ví dụ: Thuật toán và Cấu trúc dữ liệu nâng cao"
                                        {...courseForm.getInputProps("title")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        required
                                        label="Mô tả khóa học"
                                        placeholder="Mô tả chi tiết về nội dung và mục tiêu của khóa học..."
                                        rows={4}
                                        {...courseForm.getInputProps("description")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <TextInput
                                        required
                                        label="Cấp độ"
                                        placeholder="Beginner/Intermediate/Advanced"
                                        {...courseForm.getInputProps("level")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <NumberInput
                                        label="Số lượng topics tối đa"
                                        placeholder="5"
                                        min={3}
                                        max={10}
                                        {...courseForm.getInputProps("maxTopics")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <NumberInput
                                        label="Giá (VNĐ)"
                                        placeholder="0"
                                        min={0}
                                        {...courseForm.getInputProps("price")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <NumberInput
                                        label="Thời lượng (phút)"
                                        placeholder="0"
                                        min={0}
                                        {...courseForm.getInputProps("duration")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Switch
                                        label="Xuất bản khóa học ngay sau khi tạo"
                                        {...courseForm.getInputProps("isPublished", { type: "checkbox" })}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <TextInput
                                        label="Tags"
                                        placeholder="javascript,react,frontend"
                                        {...courseForm.getInputProps("tags")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Yêu cầu tiên quyết"
                                        placeholder="Các kiến thức cần có trước khi học khóa này..."
                                        rows={3}
                                        {...courseForm.getInputProps("requirements")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Những gì sẽ học được"
                                        placeholder="Học viên sẽ học được những kỹ năng gì..."
                                        rows={3}
                                        {...courseForm.getInputProps("whatYouWillLearn")}
                                    />
                                </Grid.Col>
                            </Grid>

                            <Group justify="flex-end" mt="md">
                                <Button variant="outline" onClick={handleClose}>
                                    Hủy
                                </Button>
                                <Button
                                    type="submit"
                                    leftSection={<IconTarget size={16} />}
                                    loading={isGeneratingTopics}
                                >
                                    Tạo Topics với AI
                                </Button>
                            </Group>
                        </Stack>
                    </form>
                </Stepper.Step>

                <Stepper.Step
                    label="Xem lại Topics"
                    description="Kiểm tra và chỉnh sửa topics"
                    icon={<IconEdit size={18} />}
                >
                    {generatedTopics && (
                        <Stack gap="lg">
                            <Group justify="space-between">
                                <div>
                                    <Title order={3} className="text-primary">
                                        {generatedTopics.topics.length} Topics được tạo
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

                            <Divider />

                            <Stack gap="md">
                                {generatedTopics.topics.map((topic, index) => (
                                    <Card key={index} withBorder shadow="sm" p="lg">
                                        <Group justify="space-between" mb="md">
                                            <Badge variant="filled" color="blue">
                                                Topic #{topic.order}
                                            </Badge>
                                            <ActionIcon
                                                color="red"
                                                variant="light"
                                                onClick={() => handleRemoveTopic(index)}
                                            >
                                                <IconTrash size={16} />
                                            </ActionIcon>
                                        </Group>

                                        <TextInput
                                            label="Tên topic"
                                            value={topic.name}
                                            onChange={(e) => handleEditTopic(index, 'name', e.target.value)}
                                            mb="md"
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
                                                <Text fw={500} size="sm" mb="xs">Yêu cầu tiên quyết:</Text>
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
                                            <Text fw={500} size="sm" mb="xs">
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
                                        </Box>
                                    </Card>
                                ))}
                            </Stack>

                            <Group justify="space-between" mt="xl">
                                <Button
                                    variant="outline"
                                    onClick={() => setActiveStep(0)}
                                    leftSection={<IconEdit size={16} />}
                                >
                                    Chỉnh sửa thông tin khóa học
                                </Button>
                                <Button
                                    onClick={handleCreateCourse}
                                    leftSection={<IconCheck size={16} />}
                                    loading={isCreatingCourse}
                                    color="green"
                                >
                                    Tạo khóa học và lưu Topics
                                </Button>
                            </Group>
                        </Stack>
                    )}
                </Stepper.Step>
            </Stepper>

            {/* Save Topics Modal */}
            {createdCourseId && (
                <SaveTopicsModal
                    opened={saveTopicsModalOpened}
                    onClose={() => setSaveTopicsModalOpened(false)}
                    topicsData={generatedTopics}
                    courseId={createdCourseId}
                    onSuccess={handleTopicsSaved}
                />
            )}
        </Modal>
    );
}
