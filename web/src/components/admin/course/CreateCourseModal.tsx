"use client";

import {
    Button,
    Modal,
    TextInput,
    Textarea,
    Grid,
    NumberInput,
    Switch,
    LoadingOverlay,
    Group,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { CourseCreatePayload, createCourseAdmin } from "@/lib/api/admin-courses";
import { notifications } from '@mantine/notifications';
import { useRouter } from "next/navigation";

interface CreateCourseModalProps {
    opened: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export default function CreateCourseModal({ opened, onClose, onSuccess }: CreateCourseModalProps) {
    const [isCreating, setIsCreating] = useState(false);
    const queryClient = useQueryClient();
    const router = useRouter();

    const form = useForm({
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
        },
        validate: {
            title: (value) =>
                value.length < 3 ? "Tiêu đề khóa học phải có ít nhất 3 ký tự" : null,
            description: (value) =>
                value.length < 10 ? "Mô tả khóa học phải có ít nhất 10 ký tự" : null,
        },
    });

    // Mutation for creating course
    const createCourseMutation = useMutation({
        mutationFn: async (data: CourseCreatePayload) => {
            setIsCreating(true);
            return await createCourseAdmin(data);
        },
        onSuccess: (createdCourse) => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'courses'] });
            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được tạo thành công!',
                color: 'green',
            });

            // Redirect to review page with course data
            const courseData = {
                ...form.values,
                courseId: createdCourse.id
            };

            // Store course data in sessionStorage to pass to review page
            sessionStorage.setItem('pendingCourseData', JSON.stringify(courseData));

            // Navigate to review page
            router.push(`/admin/course/${createdCourse.id}/review-topics`);

            handleClose();
            onSuccess();
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.message || 'Không thể tạo khóa học.',
                color: 'red',
            });
        },
        onSettled: () => {
            setIsCreating(false);
        }
    });

    const handleCreateCourse = async (values: typeof form.values) => {
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
        form.reset();
        onClose();
    };

    return (
        <Modal
            opened={opened}
            onClose={handleClose}
            title="Tạo khóa học mới"
            size="lg"
            closeOnClickOutside={false}
        >
            <LoadingOverlay visible={isCreating} />

            <form onSubmit={form.onSubmit(handleCreateCourse)}>
                <Grid>
                    <Grid.Col span={12}>
                        <TextInput
                            required
                            label="Tiêu đề khóa học"
                            placeholder="Ví dụ: Thuật toán và Cấu trúc dữ liệu nâng cao"
                            {...form.getInputProps("title")}
                        />
                    </Grid.Col>
                    <Grid.Col span={12}>
                        <Textarea
                            required
                            label="Mô tả khóa học"
                            placeholder="Mô tả chi tiết về nội dung và mục tiêu của khóa học..."
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
                            label="Xuất bản khóa học ngay sau khi tạo"
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
                            label="Yêu cầu tiên quyết"
                            placeholder="Các kiến thức cần có trước khi học khóa này..."
                            rows={3}
                            {...form.getInputProps("requirements")}
                        />
                    </Grid.Col>
                    <Grid.Col span={12}>
                        <Textarea
                            label="Những gì sẽ học được"
                            placeholder="Học viên sẽ học được những kỹ năng gì..."
                            rows={3}
                            {...form.getInputProps("whatYouWillLearn")}
                        />
                    </Grid.Col>
                </Grid>

                <Group justify="flex-end" mt="md">
                    <Button variant="outline" onClick={handleClose}>
                        Hủy
                    </Button>
                    <Button
                        type="submit"
                        loading={isCreating}
                    >
                        Tạo khóa học và chuyển đến Review
                    </Button>
                </Group>
            </form>
        </Modal>
    );
}
