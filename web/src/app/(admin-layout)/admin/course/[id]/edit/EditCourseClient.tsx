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
import { Course, CourseUpdatePayload } from "@/lib/api/courses";
import { getCourseByIdAdmin, updateCourseAdmin } from "@/lib/api/admin-courses";
import { uploadCourseImageAdmin, FileUploadResponse } from "@/lib/api/admin-upload";
import { notifications } from '@mantine/notifications';
import Link from "next/link";

interface EditCourseClientProps {
    courseId: number;
}

export default function EditCourseClient({ courseId }: EditCourseClientProps) {
    const [course, setCourse] = useState<Course | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Image upload states
    const [selectedImage, setSelectedImage] = useState<File | null>(null);
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [pendingImageUrl, setPendingImageUrl] = useState<string | null>(null);

    const router = useRouter();

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

    // Fetch course data
    const fetchCourse = async () => {
        try {
            setLoading(true);
            const courseData = await getCourseByIdAdmin(courseId);
            setCourse(courseData);

            // Set form values
            form.setValues({
                title: courseData.title || "",
                description: courseData.description || "",
                level: courseData.level || "Beginner",
                price: courseData.price || 0,
                duration: courseData.duration || 0,
                isPublished: courseData.isPublished || false,
                tags: courseData.tags || "",
                requirements: courseData.requirements || "",
                whatYouWillLearn: courseData.whatYouWillLearn || "",
                thumbnailUrl: courseData.thumbnailUrl || "",
            });

            setError(null);
        } catch (err: any) {
            if (err.response?.status === 404) {
                notFound();
            }
            setError("Không thể tải thông tin khóa học.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (courseId) {
            fetchCourse();
        }
    }, [courseId]);

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
        try {
            setSaving(true);

            let finalValues = { ...values };

            // Upload image first if there's a selected image
            if (selectedImage) {
                setUploading(true);
                try {
                    const uploadResult: FileUploadResponse = await uploadApi.uploadCourseImage(courseId, selectedImage);
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

            // Update course with all data including new image URL
            const updatedCourse = await coursesApi.updateCourse(courseId, finalValues);
            setCourse(updatedCourse);

            // Reset image states after successful save
            setSelectedImage(null);
            setImagePreview(null);
            setPendingImageUrl(null);

            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được cập nhật thành công!',
                color: 'green',
            });

        } catch (err: any) {
            notifications.show({
                title: 'Lỗi',
                message: err.response?.data?.detail || 'Không thể cập nhật khóa học.',
                color: 'red',
            });
            console.error(err);
        } finally {
            setSaving(false);
        }
    };

    const breadcrumbItems = [
        { title: 'Dashboard', href: '/admin' },
        { title: 'Quản lý khóa học', href: '/admin/course' },
        { title: course?.title || 'Chỉnh sửa khóa học', href: '#' },
    ].map((item, index) => (
        index < 2 ? (
            <Anchor component={Link} href={item.href} key={index}>
                {item.title}
            </Anchor>
        ) : (
            <span key={index}>{item.title}</span>
        )
    ));

    // Get current image to display
    const getCurrentImageUrl = () => {
        if (imagePreview) return imagePreview;
        if (pendingImageUrl) return pendingImageUrl;
        return course?.thumbnailUrl || null;
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
                    {error}
                </Alert>
                <Group>
                    <Button onClick={fetchCourse} variant="outline">
                        Thử lại
                    </Button>
                    <Button
                        component={Link}
                        href="/admin/course"
                        leftSection={<IconArrowLeft size={16} />}
                        variant="light"
                    >
                        Quay lại danh sách
                    </Button>
                </Group>
            </Container>
        );
    }

    return (
        <Container size="xl" className="py-8">
            <div className="space-y-6">
                <div>
                    <Breadcrumbs className="mb-4">
                        {breadcrumbItems}
                    </Breadcrumbs>

                    <Group justify="space-between" align="center" className="mb-4">
                        <div>
                            <Title order={1} className="text-3xl font-bold text-gray-900 mb-2">
                                Chỉnh sửa khóa học
                            </Title>
                            <p className="text-gray-600">
                                Cập nhật thông tin chi tiết của khóa học
                            </p>
                        </div>

                        <Button
                            component={Link}
                            href="/admin/course"
                            leftSection={<IconArrowLeft size={16} />}
                            variant="light"
                        >
                            Quay lại danh sách
                        </Button>
                    </Group>
                </div>

                <Paper shadow="sm" p="xl" withBorder className="relative">
                    <LoadingOverlay
                        visible={loading || saving}
                        overlayProps={{ radius: "sm", blur: 2 }}
                        loaderProps={{ children: saving ? 'Đang lưu...' : 'Đang tải...' }}
                    />

                    {course && (
                        <form onSubmit={form.onSubmit(handleUpdateCourse)} className="space-y-6">
                            <Title order={2} className="text-xl font-semibold mb-6">
                                Thông tin khóa học
                            </Title>

                            <Grid>
                                {/* Image Upload Section */}
                                <Grid.Col span={12}>
                                    <div className="space-y-4">
                                        <Text size="sm" fw={500} className="text-gray-700">
                                            Ảnh thumbnail
                                        </Text>

                                        {getCurrentImageUrl() && (
                                            <Box className="relative inline-block">
                                                <Image
                                                    src={getCurrentImageUrl()}
                                                    alt="Course thumbnail"
                                                    className="w-64 h-36 object-cover rounded-lg border"
                                                    fallbackSrc="/images/placeholder-course.jpg"
                                                />
                                                {(selectedImage || pendingImageUrl) && (
                                                    <ActionIcon
                                                        size="sm"
                                                        variant="filled"
                                                        color="red"
                                                        className="absolute -top-2 -right-2"
                                                        onClick={handleRemoveImage}
                                                    >
                                                        <IconX size={12} />
                                                    </ActionIcon>
                                                )}
                                                {selectedImage && (
                                                    <div className="absolute inset-0 bg-blue-500 bg-opacity-20 rounded-lg flex items-center justify-center">
                                                        <Text size="xs" className="text-blue-600 font-medium bg-white px-2 py-1 rounded">
                                                            Ảnh mới
                                                        </Text>
                                                    </div>
                                                )}
                                            </Box>
                                        )}

                                        <FileInput
                                            placeholder="Chọn ảnh thumbnail"
                                            accept="image/*"
                                            value={selectedImage}
                                            onChange={handleImageSelect}
                                            leftSection={<IconUpload size={16} />}
                                            disabled={uploading}
                                            className="max-w-md"
                                        />

                                        <Text size="xs" className="text-gray-500">
                                            Chọn ảnh để thay đổi thumbnail. Ảnh sẽ được upload khi bạn lưu thay đổi.
                                        </Text>
                                    </div>
                                </Grid.Col>

                                <Grid.Col span={6}>
                                    <TextInput
                                        label="Tiêu đề khóa học"
                                        placeholder="Nhập tiêu đề khóa học"
                                        {...form.getInputProps("title")}
                                        required
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <TextInput
                                        label="Cấp độ"
                                        placeholder="VD: Beginner, Intermediate, Advanced"
                                        {...form.getInputProps("level")}
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Mô tả"
                                        placeholder="Nhập mô tả khóa học"
                                        {...form.getInputProps("description")}
                                        rows={4}
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <NumberInput
                                        label="Giá (VNĐ)"
                                        placeholder="Nhập giá"
                                        {...form.getInputProps("price")}
                                        min={0}
                                        thousandSeparator=","
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={6}>
                                    <NumberInput
                                        label="Thời lượng (phút)"
                                        placeholder="Nhập thời lượng"
                                        {...form.getInputProps("duration")}
                                        min={0}
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <TextInput
                                        label="Thẻ tag"
                                        placeholder="Các thẻ tag cách nhau bằng dấu phẩy"
                                        {...form.getInputProps("tags")}
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Yêu cầu"
                                        placeholder="Nhập các yêu cầu cần thiết"
                                        {...form.getInputProps("requirements")}
                                        rows={3}
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Textarea
                                        label="Học viên sẽ học được gì"
                                        placeholder="Nhập những gì học viên sẽ học được"
                                        {...form.getInputProps("whatYouWillLearn")}
                                        rows={3}
                                        classNames={{
                                            label: 'font-medium text-gray-700 mb-2',
                                        }}
                                    />
                                </Grid.Col>
                                <Grid.Col span={12}>
                                    <Switch
                                        label="Xuất bản khóa học"
                                        description="Khóa học sẽ hiển thị công khai cho học viên"
                                        {...form.getInputProps("isPublished", { type: 'checkbox' })}
                                        classNames={{
                                            label: 'font-medium text-gray-700',
                                            description: 'text-gray-500 text-sm',
                                        }}
                                    />
                                </Grid.Col>
                            </Grid>

                            <Group justify="flex-end" mt="xl" className="pt-6 border-t border-gray-200">
                                <Button
                                    variant="outline"
                                    component={Link}
                                    href="/admin/course"
                                >
                                    Hủy
                                </Button>
                                <Button
                                    type="submit"
                                    leftSection={<IconDeviceFloppy size={16} />}
                                    loading={saving || uploading}
                                    className="bg-primary hover:bg-primary/90"
                                >
                                    {uploading ? 'Đang upload...' : 'Lưu thay đổi'}
                                </Button>
                            </Group>
                        </form>
                    )}
                </Paper>
            </div>
        </Container>
    );
} 