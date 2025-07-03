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
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { notFound } from "next/navigation";
import { IconArrowLeft, IconAlertCircle, IconDeviceFloppy, IconUpload, IconX, IconPhoto } from "@tabler/icons-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { UserCourseDetail, CourseUpdatePayload } from "@/lib/api/courses";
import { getCourseByIdAdmin, updateCourseAdmin, createCourseTestAdmin } from "@/lib/api/admin-courses";
import { uploadCourseImageAdmin, AdminFileUploadResponse } from "@/lib/api/admin-upload";
import { notifications } from '@mantine/notifications';
import Link from "next/link";
import TopicManagement from './TopicManagement';
import TestGenerationStatus from '@/components/admin/course/TestGenerationStatus';
import { useDragAndDrop } from '@/hooks/useDragAndDrop';

interface EditCourseClientProps {
    courseId: number;
}

export default function EditCourseClient({ courseId }: EditCourseClientProps) {
    const [topicModalOpened, setTopicModalOpened] = useState(false);

    // Image upload states
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);

    // Ref cho FileInput để có thể trigger programmatically
    const fileInputRef = useRef<HTMLButtonElement>(null);

    const router = useRouter();
    const queryClient = useQueryClient();

    // Drag and drop hook
    const { isDragOver, dragHandlers } = useDragAndDrop(
        (files: File[]) => {
            const file = files[0]; // Chỉ lấy file đầu tiên vì chỉ cho phép 1 ảnh
            if (file) {
                handleImageSelect(file);
                notifications.show({
                    title: 'Thành công',
                    message: `Đã chọn file: ${file.name}`,
                    color: 'green',
                });
            }
        },
        {
            acceptedTypes: ['image/*'],
            maxFileSize: 10 * 1024 * 1024, // 10MB
            multiple: false,
            showNotifications: true, // Hiển thị notification cho validation errors
            customValidator: (file: File) => {
                // Custom validation cho ảnh
                if (!file.type.startsWith('image/')) {
                    return 'Vui lòng chỉ chọn file ảnh (JPG, PNG, GIF).';
                }
                return null;
            }
        },
        uploading
    );

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
        refetchInterval: (data) => {
            // Auto-refresh every 10 seconds if test generation is pending
            return (data as any)?.testGenerationStatus === 'pending' ? 10000 : false;
        },
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
                    const uploadResult: AdminFileUploadResponse = await uploadCourseImageAdmin(courseId, selectedImage);

                    // Backend trả về response trực tiếp nếu thành công
                    // Update form with new image URL
                    finalValues.thumbnailUrl = uploadResult.url;
                    setImagePreview(uploadResult.url);

                    // Show success notification
                    notifications.show({
                        title: "Thành công",
                        message: "Đã tải lên ảnh khóa học thành công",
                        color: "green",
                    });
                } catch (error) {
                    notifications.show({
                        title: 'Lỗi upload ảnh',
                        message: 'Không thể upload ảnh. Vui lòng thử lại.',
                        color: 'red',
                    });
                    throw error;
                } finally {
                    setUploading(false);
                }
            }

            // Chỉ update course nếu có thay đổi form data khác (không phải chỉ ảnh)
            const hasOtherChanges = Object.keys(finalValues).some(key =>
                key !== 'thumbnailUrl' && form.isDirty(key as any)
            );

            if (hasOtherChanges || !selectedImage) {
                return await updateCourseAdmin(courseId, finalValues);
            }

            // Nếu chỉ upload ảnh thì return course hiện tại
            return course;
        },
        onSuccess: (updatedCourse) => {
            console.log('Update course success:', updatedCourse);

            // Reset image states sau khi save thành công
            setSelectedImage(null);
            setImagePreview(null);

            // Nếu có updatedCourse và nó có thumbnailUrl, cập nhật cache
            if (updatedCourse && updatedCourse.thumbnailUrl) {
                queryClient.setQueryData(['admin', 'course', courseId], updatedCourse);
                setImagePreview(null);
            } else {
                // Nếu không có thumbnailUrl trong response (trường hợp chỉ upload ảnh)
                queryClient.invalidateQueries({ queryKey: ['admin', 'course', courseId] })
                    .then(() => {
                        setTimeout(() => {
                            setImagePreview(null);
                        }, 1500);
                    });
            }

            // Also update the courses list cache if it exists
            queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });

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
            const newValues = {
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
            };

            // Set both initial values and current values, then reset to clear dirty state
            form.setInitialValues(newValues);
            form.setValues(newValues);
            form.resetDirty(newValues);

            // Chỉ reset image states khi lần đầu load course hoặc khi không có pending upload
            if (!selectedImage && !imagePreview) {
                setSelectedImage(null);
                setImagePreview(null);
                // Không reset pendingImageUrl để giữ ảnh vừa upload
                // setPendingImageUrl(null);
            }
        }
    }, [course, selectedImage, imagePreview]);

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
    };

    // Trigger file input when clicking on placeholder
    const handlePlaceholderClick = () => {
        fileInputRef.current?.click();
    };

    const handleUpdateCourse = async (values: CourseUpdatePayload) => {
        updateCourseMutation.mutate(values);
    };

    const handleGenerateTest = async () => {
        generateTestMutation.mutate();
    };

    const getCurrentImageUrl = () => {
        // Ưu tiên: imagePreview (đang chọn) > URL ảnh pending (vừa upload) > ảnh hiện tại của course
        let url = null;

        if (imagePreview) {
            // Nếu đang preview ảnh mới được chọn
            url = imagePreview;
        } else if (course?.thumbnailUrl) {
            // Ảnh hiện tại của course từ database
            url = course.thumbnailUrl;
        }
        return url;
    };

    // Debug effect để kiểm tra course data
    useEffect(() => {
        if (course) {
            console.log('Course data loaded:', {
                id: course.id,
                title: course.title,
                thumbnailUrl: course.thumbnailUrl,
                hasThumbail: !!course.thumbnailUrl
            });
        } else {
            console.log('Course data is null/undefined');
        }
    }, [course]);

    // Debug effect để theo dõi image states
    useEffect(() => {
        console.log('Image states changed:', {
            selectedImage: selectedImage?.name,
            imagePreview: !!imagePreview,
            currentUrl: getCurrentImageUrl(),
            isDragOver
        });
    }, [selectedImage, imagePreview, course?.thumbnailUrl, isDragOver]);

    // Effect để đảm bảo cache được cập nhật khi pendingImageUrl thay đổi
    useEffect(() => {
        if (!selectedImage && !course?.thumbnailUrl) {
            // Nếu có pendingImageUrl nhưng course.thumbnailUrl vẫn chưa có
            // thì refetch để có dữ liệu mới nhất
            console.log('Course thumbnailUrl still not available, refetching...');
            const timer = setTimeout(() => {
                queryClient.invalidateQueries({ queryKey: ['admin', 'course', courseId] });
            }, 1000);

            return () => clearTimeout(timer);
        }
    }, [selectedImage, course?.thumbnailUrl, courseId, queryClient]);

    // Effect để reset imagePreview khi course.thumbnailUrl đã được cập nhật
    useEffect(() => {
        if (course?.thumbnailUrl && !selectedImage) {
            // Nếu có cả imagePreview và course.thumbnailUrl, nghĩa là đã sync xong
            console.log('Course thumbnailUrl synced, resetting imagePreview');
            setTimeout(() => {
                setImagePreview(null);
            }, 500);
        }
    }, [course?.thumbnailUrl, selectedImage]);

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
                        onClick={() => form.onSubmit(handleUpdateCourse)()}
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
                        {getCurrentImageUrl() ? (
                            <Box
                                mb="md"
                                style={{ position: 'relative' }}
                                className="group"
                                {...(uploading ? {} : dragHandlers)}
                            >
                                <Image
                                    src={getCurrentImageUrl()}
                                    alt="Course thumbnail"
                                    radius="md"
                                    className={`w-full aspect-video object-cover cursor-pointer transition-all duration-200 ${isDragOver ? 'opacity-70 scale-105' : ''
                                        }`}
                                    fallbackSrc="/images/placeholder-course.jpg"
                                    onClick={handlePlaceholderClick}
                                />

                                {/* Drag overlay */}
                                {isDragOver && (
                                    <Box
                                        style={{
                                            position: 'absolute',
                                            top: 0,
                                            left: 0,
                                            right: 0,
                                            bottom: 0,
                                            backgroundColor: 'rgba(59, 130, 246, 0.9)',
                                            borderRadius: '8px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            zIndex: 5,
                                        }}
                                    >
                                        <div className="text-center text-white">
                                            <IconPhoto size={48} className="mx-auto mb-2" />
                                            <Text size="lg" fw={600} color="white">
                                                Thả ảnh mới vào đây
                                            </Text>
                                            <Text size="sm" color="white" opacity={0.9}>
                                                Sẽ thay thế ảnh hiện tại
                                            </Text>
                                        </div>
                                    </Box>
                                )}
                                <ActionIcon
                                    size="lg"
                                    variant="filled"
                                    onClick={handleRemoveImage}
                                    style={{
                                        position: 'absolute',
                                        top: '8px',
                                        right: '8px',
                                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                        border: '2px solid rgba(239, 68, 68, 0.2)',
                                        borderRadius: '50%',
                                        zIndex: 10,
                                        opacity: 0.9,
                                        transition: 'all 0.2s ease',
                                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.opacity = '1';
                                        e.currentTarget.style.transform = 'scale(1.1)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.opacity = '0.9';
                                        e.currentTarget.style.transform = 'scale(1)';
                                    }}
                                >
                                    <IconX size={18} color="#ef4444" />
                                </ActionIcon>
                            </Box>
                        ) : (
                            <Box
                                mb="md"
                                className={`w-full aspect-video rounded-md flex items-center justify-center transition-all duration-200 ${uploading
                                    ? 'cursor-not-allowed opacity-50 bg-gray-100 border-2 border-dashed border-gray-300'
                                    : isDragOver
                                        ? 'cursor-pointer bg-blue-50 border-2 border-dashed border-blue-400 transform scale-105'
                                        : 'cursor-pointer bg-gray-100 border-2 border-dashed border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                                    }`}
                                onClick={uploading ? undefined : handlePlaceholderClick}
                                {...(uploading ? {} : dragHandlers)}
                            >
                                <div className="text-center">
                                    {uploading ? (
                                        <>
                                            <div className="animate-spin text-4xl mb-2">⏳</div>
                                            <Text size="sm" c="dimmed">
                                                Đang upload ảnh...
                                            </Text>
                                        </>
                                    ) : isDragOver ? (
                                        <>
                                            <IconPhoto size={48} className="mx-auto mb-2 text-blue-500" />
                                            <Text size="sm" c="blue" fw={500}>
                                                Thả ảnh vào đây
                                            </Text>
                                            <Text size="xs" c="blue">
                                                JPG, PNG, GIF tối đa 10MB
                                            </Text>
                                        </>
                                    ) : (
                                        <>
                                            <IconPhoto size={48} className="mx-auto mb-2 text-gray-400" />
                                            <Text size="sm" c="dimmed">
                                                Nhấn hoặc kéo thả ảnh vào đây
                                            </Text>
                                            <Text size="xs" c="dimmed">
                                                JPG, PNG, GIF tối đa 10MB
                                            </Text>
                                        </>
                                    )}
                                </div>
                            </Box>
                        )}

                        {/* Hidden FileInput - chỉ dùng để trigger dialog */}
                        <FileInput
                            placeholder="Chọn file ảnh..."
                            accept="image/*"
                            leftSection={<IconUpload size={14} />}
                            value={selectedImage}
                            onChange={handleImageSelect}
                            disabled={uploading}
                            ref={fileInputRef}
                            style={{ display: 'none' }}
                        />

                        {/* Upload progress hoặc info */}
                        {uploading && (
                            <Box p="xs" className="bg-yellow-50 rounded border border-yellow-200">
                                <Group gap="xs">
                                    <div className="animate-spin">⏳</div>
                                    <Text size="sm" fw={500} c="yellow.7">
                                        Đang upload ảnh...
                                    </Text>
                                </Group>
                            </Box>
                        )}

                        {selectedImage && !uploading && (
                            <Box p="xs" className="bg-blue-50 rounded border border-blue-200">
                                <Text size="sm" fw={500} c="blue">
                                    📁 {selectedImage.name}
                                </Text>
                                <Text size="xs" c="dimmed">
                                    Ảnh sẽ được upload khi lưu khóa học
                                </Text>
                            </Box>
                        )}

                        {course?.thumbnailUrl && !selectedImage && !uploading && (
                            <Box p="xs" className="bg-green-50 rounded border border-green-200">
                                <Text size="xs" c="green" fw={500}>
                                    ✓ Ảnh hiện tại: {course.thumbnailUrl.split('/').pop()}
                                </Text>
                                <Text size="xs" c="dimmed">
                                    Nhấn vào ảnh phía trên để thay đổi
                                </Text>
                            </Box>
                        )}

                        {/* Debug info trong development */}
                        {process.env.NODE_ENV === 'development' && (
                            <Box mt="xs" p="xs" className="bg-gray-50 rounded text-xs">
                                <Text size="xs" fw={500} mb={4}>Debug Info:</Text>
                                <Text size="xs">Course ID: {course?.id}</Text>
                                <Text size="xs">Thumbnail URL: {course?.thumbnailUrl || 'null'}</Text>
                                <Text size="xs">Current URL: {getCurrentImageUrl() || 'null'}</Text>
                                <Text size="xs">Image Preview: {imagePreview ? 'có' : 'không'}</Text>
                                <Text size="xs">Selected Image: {selectedImage?.name || 'không'}</Text>
                            </Box>
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