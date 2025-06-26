"use client";

import {
    Button,
    TextInput,
    Textarea,
    Title,
    Paper,
    Container,
    Group,
    Grid,
    NumberInput,
    Switch,
    LoadingOverlay,
    Alert,
    Breadcrumbs,
    Anchor,
    FileInput,
    Image,
    Text,
    ActionIcon,
    Box,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";
import { IconArrowLeft, IconAlertCircle, IconDeviceFloppy, IconUpload, IconX, IconPhoto } from "@tabler/icons-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Course, CourseUpdatePayload } from "@/lib/api/courses";
import { getCourseByIdAdmin, updateCourseAdmin, createCourseTestAdmin } from "@/lib/api/admin-courses";
import { uploadCourseImageAdmin, FileUploadResponse } from "@/lib/api/admin-upload";
import { notifications } from '@mantine/notifications';
import Link from "next/link";
import TopicManagement from './TopicManagement';
import TestGenerationStatus from '@/components/admin/course/TestGenerationStatus';

interface EditCourseClientProps {
    courseId: number;
}

export default function EditCourseClient({ courseId }: EditCourseClientProps) {
    const [topicModalOpened, setTopicModalOpened] = useState(false);

    // Image upload states
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [pendingImageUrl, setPendingImageUrl] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);

    const router = useRouter();
    const queryClient = useQueryClient();

    // Use useQuery to cache course data
    const {
        data: course,
        isLoading: loading,
        error,
        refetch: fetchCourse
    } = useQuery({
        queryKey: ['admin', 'course', courseId],
        queryFn: async () => {
            if (!courseId) throw new Error('Course ID is required');
            return await getCourseByIdAdmin(courseId);
        },
        enabled: !!courseId,
        staleTime: 2 * 60 * 1000, // Cache for 2 minutes
        retry: (failureCount, error: any) => {
            if (error?.response?.status === 404) {
                notFound();
                return false;
            }
            return failureCount < 3;
        },
    });

    // Mutation for updating course
    const updateCourseMutation = useMutation({
        mutationFn: async (values: CourseUpdatePayload) => {
            let finalValues = { ...values };

            // Upload image first if there's a selected image
            if (selectedImage) {
                setUploading(true);
                try {
                    const uploadResult: FileUploadResponse = await uploadCourseImageAdmin(courseId, selectedImage);
                    finalValues.thumbnailUrl = uploadResult.url;
                    setPendingImageUrl(uploadResult.url);
                } catch (uploadError) {
                    notifications.show({
                        title: 'Lỗi upload ảnh',
                        message: 'Không thể upload ảnh. Vui lòng thử lại.',
                        color: 'red',
                    });
                    throw uploadError;
                } finally {
                    setUploading(false);
                }
            }

            return await updateCourseAdmin(courseId, finalValues);
        },
        onSuccess: (updatedCourse) => {
            // Update cache with new course data
            queryClient.setQueryData(['admin', 'course', courseId], updatedCourse);

            // Also update the courses list cache if it exists
            queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });

            // Reset image states after successful save
            setSelectedImage(null);
            setImagePreview(null);
            setPendingImageUrl(null);

            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được cập nhật thành công!',
                color: 'green',
            });
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.response?.data?.detail || 'Không thể cập nhật khóa học.',
                color: 'red',
            });
            console.error(err);
        }
    });

    // Mutation for generating test (realtime, không cache)
    const generateTestMutation = useMutation({
        mutationFn: () => createCourseTestAdmin(courseId),
        onSuccess: () => {
            notifications.show({
                title: 'Thành công',
                message: 'Đã bắt đầu tạo bài test. Quá trình có thể mất vài phút.',
                color: 'green',
            });

            // Invalidate course data to get updated test status
            queryClient.invalidateQueries({ queryKey: ['admin', 'course', courseId] });
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.response?.data?.detail || 'Không thể tạo bài test.',
                color: 'red',
            });
            console.error(err);
        }
    });

    const form = useForm<CourseUpdatePayload>({
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
            thumbnailUrl: "",
        },
        validate: {
            title: (value) =>
                value && value.length < 3 ? "Tiêu đề khóa học phải có ít nhất 3 ký tự" : null,
        },
    });

    // Update form when course data changes
    useEffect(() => {
        if (course) {
            form.setValues({
                title: course.title || "",
                description: course.description || "",
                level: course.level || "Beginner",
                price: course.price || 0,
                duration: course.duration || 0,
                isPublished: course.isPublished || false,
                tags: course.tags || "",
                requirements: course.requirements || "",
                whatYouWillLearn: course.whatYouWillLearn || "",
                thumbnailUrl: course.thumbnailUrl || "",
            });
        }
    }, [course]);

    // Handle image file selection
    const handleImageSelect = (file: File | null) => {
        setSelectedImage(file);
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                setImagePreview(e.target?.result as string);
            };
            reader.readAsDataURL(file);
        } else {
            setImagePreview(null);
        }
    };

    // Remove selected image
    const handleRemoveImage = () => {
        setSelectedImage(null);
        setImagePreview(null);
        setPendingImageUrl(null);
    };

    const handleUpdateCourse = async (values: CourseUpdatePayload) => {
        updateCourseMutation.mutate(values);
    };

    const handleGenerateTest = async () => {
        generateTestMutation.mutate();
    };

    const getCurrentImageUrl = () => {
        return pendingImageUrl || course?.thumbnailUrl || null;
    };

    if (error) {
        return (
            <Container size="xl" className="py-8">
                <Alert
                    icon={<IconAlertCircle size="1rem" />}
                    title="Lỗi!"
                    color="red"
                    className="mb-4"
                >
                    {error.message || "Không thể tải thông tin khóa học."}
                </Alert>
                <Button onClick={() => fetchCourse()} variant="outline">
                    Thử lại
                </Button>
            </Container>
        );
    }

    const breadcrumbItems = [
        { title: 'Trang chủ', href: '/admin' },
        { title: 'Khóa học', href: '/admin/course' },
        { title: course?.title || 'Đang tải...', href: '#' },
    ].map((item, index) => (
        <Anchor component={Link} href={item.href} key={index}>
            {item.title}
        </Anchor>
    ));

    return (
        <Container size="xl" className="py-8">
            <LoadingOverlay visible={loading} />

            {/* Breadcrumbs */}
            <Breadcrumbs mb="lg">{breadcrumbItems}</Breadcrumbs>

            {/* Header */}
            <Group justify="space-between" mb="xl">
                <Group>
                    <ActionIcon
                        variant="light"
                        size="lg"
                        onClick={() => router.push('/admin/course')}
                    >
                        <IconArrowLeft size={20} />
                    </ActionIcon>
                    <div>
                        <Title order={2} className="text-gray-800">
                            Chỉnh sửa khóa học
                        </Title>
                        <Text size="sm" c="dimmed">
                            ID: {courseId} • {course?.isPublished ? 'Đã xuất bản' : 'Nháp'}
                        </Text>
                    </div>
                </Group>

                <Group>
                    <Button
                        variant="outline"
                        onClick={() => setTopicModalOpened(true)}
                    >
                        Quản lý Topics
                    </Button>
                    <Button
                        leftSection={<IconDeviceFloppy size={16} />}
                        onClick={form.onSubmit(handleUpdateCourse)}
                        loading={updateCourseMutation.isPending || uploading}
                        disabled={!form.isDirty() && !selectedImage}
                    >
                        Lưu thay đổi
                    </Button>
                </Group>
            </Group>

            <Grid>
                {/* Main form */}
                <Grid.Col span={{ base: 12, md: 8 }}>
                    <Paper p="xl" shadow="sm">
                        <form onSubmit={form.onSubmit(handleUpdateCourse)}>
                            <Grid>
                                <Grid.Col span={12}>
                                    <TextInput
                                        required
                                        label="Tiêu đề khóa học"
                                        placeholder="Nhập tiêu đề..."
                                        {...form.getInputProps("title")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Mô tả"
                                        placeholder="Mô tả khóa học..."
                                        rows={4}
                                        {...form.getInputProps("description")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <TextInput
                                        required
                                        label="Cấp độ"
                                        placeholder="Beginner/Intermediate/Advanced"
                                        {...form.getInputProps("level")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <NumberInput
                                        label="Giá (VNĐ)"
                                        placeholder="0"
                                        min={0}
                                        {...form.getInputProps("price")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <NumberInput
                                        label="Thời lượng (phút)"
                                        placeholder="0"
                                        min={0}
                                        {...form.getInputProps("duration")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <Switch
                                        label="Xuất bản khóa học"
                                        {...form.getInputProps("isPublished", { type: "checkbox" })}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <TextInput
                                        label="Tags"
                                        placeholder="javascript,react,frontend"
                                        {...form.getInputProps("tags")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Yêu cầu"
                                        placeholder="Các yêu cầu trước khi học..."
                                        rows={3}
                                        {...form.getInputProps("requirements")}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Những gì sẽ học được"
                                        placeholder="Học viên sẽ học được..."
                                        rows={3}
                                        {...form.getInputProps("whatYouWillLearn")}
                                    />
                                </Grid.Col>
                            </Grid>
                        </form>
                    </Paper>
                </Grid.Col>

                {/* Sidebar */}
                <Grid.Col span={{ base: 12, md: 4 }}>
                    {/* Course Image */}
                    <Paper p="lg" shadow="sm" mb="md">
                        <Title order={4} mb="md">Ảnh khóa học</Title>

                        {/* Current or preview image */}
                        {(imagePreview || getCurrentImageUrl()) && (
                            <Box mb="md" className="relative">
                                <Image
                                    src={imagePreview || getCurrentImageUrl()}
                                    alt="Course thumbnail"
                                    radius="md"
                                    className="w-full aspect-video object-cover"
                                />
                                <ActionIcon
                                    color="red"
                                    size="sm"
                                    className="absolute top-2 right-2"
                                    onClick={handleRemoveImage}
                                >
                                    <IconX size={14} />
                                </ActionIcon>
                            </Box>
                        )}

                        <FileInput
                            label="Upload ảnh mới"
                            placeholder="Chọn file ảnh..."
                            accept="image/*"
                            leftSection={<IconUpload size={14} />}
                            value={selectedImage}
                            onChange={handleImageSelect}
                            disabled={uploading}
                        />

                        {selectedImage && (
                            <Text size="xs" c="dimmed" mt="xs">
                                Ảnh sẽ được upload khi lưu khóa học
                            </Text>
                        )}
                    </Paper>

                    {/* Test Generation Status */}
                    <Paper p="lg" shadow="sm">
                        <Title order={4} mb="md">Test đầu vào</Title>
                        <TestGenerationStatus
                            status={course?.testGenerationStatus || 'not_started'}
                            onGenerateTest={handleGenerateTest}
                            loading={generateTestMutation.isPending}
                        />
                    </Paper>
                </Grid.Col>
            </Grid>

            {/* Topic Management Modal */}
            <TopicManagement
                courseId={courseId}
                opened={topicModalOpened}
                onClose={() => setTopicModalOpened(false)}
            />
        </Container>
    );
} 