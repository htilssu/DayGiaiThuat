"use client";

import {
    Button,
    Modal,
    Table,
    TextInput,
    Textarea,
    Title,
    Paper,
    Container,
    Group,
    Accordion,
    ActionIcon,
    Tooltip,
    Grid,
    NumberInput,
    Switch,
    LoadingOverlay,
    Alert,
    Checkbox,
    Text,
    Divider,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useDisclosure } from "@mantine/hooks";
import { IconPlus, IconChevronRight, IconPencil, IconTrash, IconAlertCircle } from "@tabler/icons-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Course, CourseCreatePayload, getAllCoursesAdmin, createCourseAdmin, deleteCourseAdmin, bulkDeleteCoursesAdmin } from "@/lib/api/admin-courses";
import { AdminTopic } from "@/lib/api/admin-topics";
import { notifications } from '@mantine/notifications';
import TestGenerationStatus from './TestGenerationStatus';

export default function CourseAdminClient() {
    const [opened, { open, close }] = useDisclosure(false);
    const [selectedCourses, setSelectedCourses] = useState<number[]>([]);
    const [bulkDeleteModalOpened, { open: openBulkDeleteModal, close: closeBulkDeleteModal }] = useDisclosure(false);
    const router = useRouter();
    const queryClient = useQueryClient();

    // Use useQuery to cache courses data
    const {
        data: courses = [],
        isLoading: loading,
        error,
        refetch: fetchCourses
    } = useQuery({
        queryKey: ['admin', 'courses'],
        queryFn: async () => {
            return await getAllCoursesAdmin();
        },
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
        retry: 3,
    });

    // Mutation for creating courses
    const createCourseMutation = useMutation({
        mutationFn: createCourseAdmin,
        onSuccess: (newCourse) => {
            // Update cache with new course
            queryClient.setQueryData(['admin', 'courses'], (old: Course[] = []) => [...old, newCourse]);
            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được tạo thành công!',
                color: 'green',
            });
            close();
            form.reset();
        },
        onError: (err) => {
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể tạo khóa học.',
                color: 'red',
            });
            console.error(err);
        }
    });

    // Mutation for deleting courses
    const deleteCourseMutation = useMutation({
        mutationFn: deleteCourseAdmin,
        onSuccess: (_, courseId) => {
            // Update cache by removing deleted course
            queryClient.setQueryData(['admin', 'courses'], (old: Course[] = []) =>
                old.filter(course => course.id !== courseId)
            );
            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được xóa thành công!',
                color: 'green',
            });
        },
        onError: (err) => {
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể xóa khóa học.',
                color: 'red',
            });
            console.error(err);
        }
    });

    // Mutation for bulk deleting courses
    const bulkDeleteMutation = useMutation({
        mutationFn: bulkDeleteCoursesAdmin,
        onSuccess: (result) => {
            // Update cache by removing deleted courses
            queryClient.setQueryData(['admin', 'courses'], (old: Course[] = []) =>
                old.filter(course => !result.deletedCourses.includes(course.id))
            );

            // Show success notification
            notifications.show({
                title: 'Thành công',
                message: `Đã xóa ${result.deletedCount} khóa học thành công!`,
                color: 'green',
            });

            // Show errors if any
            if (result.failedCount > 0) {
                notifications.show({
                    title: 'Cảnh báo',
                    message: `${result.failedCount} khóa học không thể xóa.`,
                    color: 'yellow',
                });
                console.error('Bulk delete errors:', result.errors);
            }

            // Reset selections and close modal
            setSelectedCourses([]);
            closeBulkDeleteModal();
        },
        onError: (err) => {
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể xóa khóa học.',
                color: 'red',
            });
            console.error(err);
        }
    });

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
        },
    });

    const handleCreateCourse = async (values: CourseCreatePayload) => {
        createCourseMutation.mutate(values);
    };

    const handleDeleteCourse = async (courseId: number) => {
        if (confirm('Bạn có chắc chắn muốn xóa khóa học này không?')) {
            deleteCourseMutation.mutate(courseId);
        }
    };

    const handleSelectCourse = (courseId: number, checked: boolean) => {
        if (checked) {
            setSelectedCourses(prev => [...prev, courseId]);
        } else {
            setSelectedCourses(prev => prev.filter(id => id !== courseId));
        }
    };

    const handleSelectAll = (checked: boolean) => {
        if (checked) {
            setSelectedCourses(courses.map(course => course.id));
        } else {
            setSelectedCourses([]);
        }
    };

    const handleBulkDelete = () => {
        if (selectedCourses.length === 0) {
            notifications.show({
                title: 'Cảnh báo',
                message: 'Vui lòng chọn ít nhất một khóa học để xóa.',
                color: 'yellow',
            });
            return;
        }
        openBulkDeleteModal();
    };

    const confirmBulkDelete = () => {
        bulkDeleteMutation.mutate(selectedCourses);
    };

    const courseRows = courses.map((course) => (
        <Table.Tr key={course.id}>
            <Table.Td>
                <Checkbox
                    checked={selectedCourses.includes(course.id)}
                    onChange={(event) => handleSelectCourse(course.id, event.currentTarget.checked)}
                />
            </Table.Td>
            <Table.Td>{course.id}</Table.Td>
            <Table.Td>
                <div>
                    <div className="font-medium text-gray-900">{course.title}</div>
                    {course.description && (
                        <div className="text-sm text-gray-500 mt-1 line-clamp-2 md:max-w-64">
                            {course.description}
                        </div>
                    )}
                </div>
            </Table.Td>
            <Table.Td>
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${course.level === 'Beginner' ? 'bg-green-100 text-green-800' :
                    course.level === 'Intermediate' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                    }`}>
                    {course.level}
                </span>
            </Table.Td>
            <Table.Td>
                <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${course.isPublished ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                    }`}>
                    {course.isPublished ? 'Đã xuất bản' : 'Nháp'}
                </span>
            </Table.Td>
            <Table.Td>
                <TestGenerationStatus
                    status={course.testGenerationStatus || 'not_started'}
                />
            </Table.Td>
            <Table.Td>
                <span className="text-sm font-medium text-green-600">
                    {course.price === 0 ? 'Miễn phí' : `${course.price.toLocaleString()}₫`}
                </span>
            </Table.Td>
            <Table.Td>
                <Group gap="xs">
                    <Tooltip label="Chỉnh sửa khóa học">
                        <ActionIcon
                            variant="light"
                            color="blue"
                            size="sm"
                            onClick={() => router.push(`/admin/course/${course.id}/edit`)}
                        >
                            <IconPencil size={14} />
                        </ActionIcon>
                    </Tooltip>
                    <Tooltip label="Xóa khóa học">
                        <ActionIcon
                            variant="light"
                            color="red"
                            size="sm"
                            onClick={() => handleDeleteCourse(course.id)}
                            loading={deleteCourseMutation.isPending}
                        >
                            <IconTrash size={14} />
                        </ActionIcon>
                    </Tooltip>
                </Group>
            </Table.Td>
        </Table.Tr>
    ));

    if (error) {
        return (
            <Container size="xl" className="py-8">
                <Alert
                    icon={<IconAlertCircle size="1rem" />}
                    title="Lỗi!"
                    color="red"
                    className="mb-4"
                >
                    {error.message || 'Không thể tải danh sách khóa học.'}
                </Alert>
                <Button onClick={() => fetchCourses()} variant="outline">
                    Thử lại
                </Button>
            </Container>
        );
    }

    return (
        <Container size="xl" className="py-8">
            <LoadingOverlay visible={loading} />

            <Paper p="xl" shadow="sm" className="relative">
                <Group justify="space-between" mb="xl">
                    <Title order={2} className="text-gray-800">
                        Quản lý Khóa học
                    </Title>
                    <Group>
                        {selectedCourses.length > 0 && (
                            <Button
                                color="red"
                                variant="light"
                                leftSection={<IconTrash size={16} />}
                                onClick={handleBulkDelete}
                                loading={bulkDeleteMutation.isPending}
                            >
                                Xóa {selectedCourses.length} khóa học
                            </Button>
                        )}
                        <Button
                            leftSection={<IconPlus size={16} />}
                            onClick={open}
                            loading={createCourseMutation.isPending}
                        >
                            Tạo khóa học mới
                        </Button>
                    </Group>
                </Group>

                <Table>
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>
                                <Checkbox
                                    checked={selectedCourses.length === courses.length && courses.length > 0}
                                    indeterminate={selectedCourses.length > 0 && selectedCourses.length < courses.length}
                                    onChange={(event) => handleSelectAll(event.currentTarget.checked)}
                                />
                            </Table.Th>
                            <Table.Th>ID</Table.Th>
                            <Table.Th>Thông tin khóa học</Table.Th>
                            <Table.Th>Cấp độ</Table.Th>
                            <Table.Th>Trạng thái</Table.Th>
                            <Table.Th>Test đầu vào</Table.Th>
                            <Table.Th>Giá</Table.Th>
                            <Table.Th>Hành động</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>{courseRows}</Table.Tbody>
                </Table>

                <Modal
                    opened={opened}
                    onClose={close}
                    title="Tạo khóa học mới"
                    size="lg"
                >
                    <form onSubmit={form.onSubmit(handleCreateCourse)}>
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

                        <Group justify="flex-end" mt="md">
                            <Button variant="outline" onClick={close}>
                                Hủy
                            </Button>
                            <Button
                                type="submit"
                                loading={createCourseMutation.isPending}
                            >
                                Tạo khóa học
                            </Button>
                        </Group>
                    </form>
                </Modal>

                {/* Bulk Delete Confirmation Modal */}
                <Modal
                    opened={bulkDeleteModalOpened}
                    onClose={closeBulkDeleteModal}
                    title="Xác nhận xóa nhiều khóa học"
                    size="md"
                >
                    <Text mb="md">
                        Bạn có chắc chắn muốn xóa <strong>{selectedCourses.length}</strong> khóa học đã chọn không?
                    </Text>
                    <Text size="sm" c="dimmed" mb="xl">
                        Hành động này không thể hoàn tác. Các khóa học đang có học viên đăng ký sẽ không thể xóa.
                    </Text>

                    <Group justify="flex-end">
                        <Button
                            variant="outline"
                            onClick={closeBulkDeleteModal}
                            disabled={bulkDeleteMutation.isPending}
                        >
                            Hủy
                        </Button>
                        <Button
                            color="red"
                            onClick={confirmBulkDelete}
                            loading={bulkDeleteMutation.isPending}
                        >
                            Xóa {selectedCourses.length} khóa học
                        </Button>
                    </Group>
                </Modal>
            </Paper>
        </Container>
    );
} 