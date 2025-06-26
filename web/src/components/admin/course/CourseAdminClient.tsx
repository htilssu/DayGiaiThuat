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
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useDisclosure } from "@mantine/hooks";
import { IconPlus, IconChevronRight, IconPencil, IconTrash, IconAlertCircle } from "@tabler/icons-react";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Course, CourseCreatePayload } from "@/lib/api/courses";
import { getAllCoursesAdmin, createCourseAdmin, deleteCourseAdmin } from "@/lib/api/admin-courses";
import { Topic } from "@/lib/api/admin-topics";
import { notifications } from '@mantine/notifications';

export default function CourseAdminClient() {
    const [courses, setCourses] = useState<Course[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [opened, { open, close }] = useDisclosure(false);
    const router = useRouter();

    const fetchCourses = async () => {
        try {
            setLoading(true);
            const courses = await getAllCoursesAdmin(); // Admin có thể xem tất cả khóa học
            setCourses(courses);
            setError(null);
        } catch (err) {
            setError("Không thể tải danh sách khóa học.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCourses();
    }, []);

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
        try {
            const newCourse = await createCourseAdmin(values);
            setCourses((prev) => [...prev, newCourse]);
            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được tạo thành công!',
                color: 'green',
            });
            close();
            form.reset();
        } catch (err) {
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể tạo khóa học.',
                color: 'red',
            });
            console.error(err);
        }
    };

    const handleDeleteCourse = async (courseId: number) => {
        try {
            await deleteCourseAdmin(courseId);
            setCourses((prev) => prev.filter(course => course.id !== courseId));
            notifications.show({
                title: 'Thành công',
                message: 'Khóa học đã được xóa thành công!',
                color: 'green',
            });
        } catch (err) {
            notifications.show({
                title: 'Lỗi',
                message: 'Không thể xóa khóa học.',
                color: 'red',
            });
            console.error(err);
        }
    };

    const courseRows = courses.map((course) => (
        <Table.Tr key={course.id}>
            <Table.Td>{course.id}</Table.Td>
            <Table.Td>
                <div>
                    <div className="font-medium text-gray-900">{course.title}</div>
                    {course.description && (
                        <div className="text-sm text-gray-500 mt-1 line-clamp-2">
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
                            onClick={() => {
                                if (confirm('Bạn có chắc chắn muốn xóa khóa học này không?')) {
                                    handleDeleteCourse(course.id);
                                }
                            }}
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
                    {error}
                </Alert>
                <Button onClick={fetchCourses} variant="outline">
                    Thử lại
                </Button>
            </Container>
        );
    }

    return (
        <Container size="xl" className="py-8">
            <div className="space-y-6">
                <div>
                    <Title order={1} className="text-3xl font-bold text-gray-900 mb-2">
                        Quản lý Khóa học
                    </Title>
                    <p className="text-gray-600">
                        Tạo và quản lý các khóa học cùng với chủ đề của chúng
                    </p>
                </div>

                <Paper shadow="sm" p="xl" withBorder className="relative">
                    <LoadingOverlay visible={loading} overlayProps={{ radius: "sm", blur: 2 }} />

                    <Group justify="space-between" mb="lg">
                        <Title order={2} className="text-xl font-semibold">
                            Tất cả khóa học ({courses.length})
                        </Title>
                        <Button
                            onClick={open}
                            leftSection={<IconPlus size={16} />}
                            className="bg-primary hover:bg-primary/90"
                        >
                            Tạo khóa học mới
                        </Button>
                    </Group>

                    {courses.length === 0 && !loading ? (
                        <div className="text-center py-12">
                            <IconAlertCircle size={48} className="mx-auto text-gray-400 mb-4" />
                            <Title order={3} className="text-gray-500 mb-2">Chưa có khóa học nào</Title>
                            <p className="text-gray-400 mb-4">Hãy tạo khóa học đầu tiên của bạn</p>
                            <Button onClick={open} leftSection={<IconPlus size={16} />}>
                                Tạo khóa học mới
                            </Button>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <Table striped highlightOnHover verticalSpacing="md">
                                <Table.Thead>
                                    <Table.Tr>
                                        <Table.Th>ID</Table.Th>
                                        <Table.Th>Thông tin khóa học</Table.Th>
                                        <Table.Th>Cấp độ</Table.Th>
                                        <Table.Th>Trạng thái</Table.Th>
                                        <Table.Th>Giá</Table.Th>
                                        <Table.Th>Thao tác</Table.Th>
                                    </Table.Tr>
                                </Table.Thead>
                                <Table.Tbody>{courseRows}</Table.Tbody>
                            </Table>
                        </div>
                    )}
                </Paper>
            </div>

            <Modal
                opened={opened}
                onClose={close}
                title={
                    <Title order={3} className="text-xl font-semibold">
                        Tạo khóa học mới
                    </Title>
                }
                centered
                size="lg"
                padding="xl"
            >
                <form onSubmit={form.onSubmit(handleCreateCourse)} className="space-y-4">
                    <Grid>
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
                                rows={3}
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
                                placeholder="Nhập các yêu cầu cần thiết (chuỗi JSON)"
                                {...form.getInputProps("requirements")}
                                rows={2}
                                classNames={{
                                    label: 'font-medium text-gray-700 mb-2',
                                }}
                            />
                        </Grid.Col>
                        <Grid.Col span={12}>
                            <Textarea
                                label="Học viên sẽ học được gì"
                                placeholder="Nhập những gì học viên sẽ học được (chuỗi JSON)"
                                {...form.getInputProps("whatYouWillLearn")}
                                rows={2}
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
                    <Button
                        type="submit"
                        mt="xl"
                        fullWidth
                        size="md"
                        className="bg-primary hover:bg-primary/90"
                    >
                        Tạo khóa học
                    </Button>
                </form>
            </Modal>
        </Container>
    );
} 