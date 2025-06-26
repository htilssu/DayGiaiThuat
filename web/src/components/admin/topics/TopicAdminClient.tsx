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
    Table,
    ActionIcon,
    Modal,
    Select,
    Text,
    Alert,
    Badge,
    Box,
    Pagination,
    LoadingOverlay,
    Menu,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { useState } from "react";
import {
    IconPlus,
    IconEdit,
    IconTrash,
    IconSearch,
    IconAlertCircle,
    IconDots,
    IconBook,
} from "@tabler/icons-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { notifications } from '@mantine/notifications';
import {
    getAllTopicsAdmin,
    createTopicAdmin,
    updateTopicAdmin,
    deleteTopicAdmin,
    assignTopicToCourseAdmin,
    type Topic,
    type TopicCreatePayload,
    type TopicUpdatePayload
} from "@/lib/api/admin-topics";
import { getAllCoursesAdmin } from "@/lib/api/admin-courses";

interface TopicFormData {
    name: string;
    description: string;
    courseId: number | null;
}

export default function TopicAdminClient() {
    const [searchQuery, setSearchQuery] = useState("");
    const [page, setPage] = useState(1);
    const [createModalOpened, setCreateModalOpened] = useState(false);
    const [editModalOpened, setEditModalOpened] = useState(false);
    const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
    const [deleteModalOpened, setDeleteModalOpened] = useState(false);

    const queryClient = useQueryClient();
    const itemsPerPage = 10;

    // Fetch topics
    const { data: topics = [], isLoading: loadingTopics } = useQuery({
        queryKey: ['admin', 'topics', 'all'],
        queryFn: getAllTopicsAdmin,
        staleTime: 2 * 60 * 1000, // Cache for 2 minutes
    });

    // Fetch courses for dropdown
    const { data: courses = [] } = useQuery({
        queryKey: ['admin', 'courses'],
        queryFn: getAllCoursesAdmin,
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    });

    // Filter and paginate topics
    const filteredTopics = topics.filter(topic =>
        topic.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (topic.description && topic.description.toLowerCase().includes(searchQuery.toLowerCase()))
    );

    const totalPages = Math.ceil(filteredTopics.length / itemsPerPage);
    const paginatedTopics = filteredTopics.slice(
        (page - 1) * itemsPerPage,
        page * itemsPerPage
    );

    // Create topic form
    const createForm = useForm<TopicFormData>({
        initialValues: {
            name: "",
            description: "",
            courseId: null,
        },
        validate: {
            name: (value) => value.trim().length < 1 ? "Tên topic không được để trống" : null,
            courseId: (value) => value === null ? "Vui lòng chọn khóa học" : null,
        },
    });

    // Edit topic form
    const editForm = useForm<TopicFormData>({
        initialValues: {
            name: "",
            description: "",
            courseId: null,
        },
        validate: {
            name: (value) => value.trim().length < 1 ? "Tên topic không được để trống" : null,
        },
    });

    // Create mutation
    const createMutation = useMutation({
        mutationFn: async (values: TopicFormData) => {
            const payload: TopicCreatePayload = {
                name: values.name,
                description: values.description,
                courseId: values.courseId!,
            };
            return await createTopicAdmin(payload);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'topics'] });
            setCreateModalOpened(false);
            createForm.reset();
            notifications.show({
                title: 'Thành công',
                message: 'Topic đã được tạo thành công!',
                color: 'green',
            });
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.response?.data?.detail || 'Không thể tạo topic.',
                color: 'red',
            });
        }
    });

    // Update mutation
    const updateMutation = useMutation({
        mutationFn: async (values: TopicFormData) => {
            if (!selectedTopic) return;

            const payload: TopicUpdatePayload = {
                name: values.name,
                description: values.description,
            };

            const updatedTopic = await updateTopicAdmin(selectedTopic.id, payload);

            // If courseId changed, assign to new course
            if (values.courseId !== selectedTopic.courseId) {
                await assignTopicToCourseAdmin(selectedTopic.id, {
                    courseId: values.courseId,
                });
            }

            return updatedTopic;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'topics'] });
            setEditModalOpened(false);
            setSelectedTopic(null);
            editForm.reset();
            notifications.show({
                title: 'Thành công',
                message: 'Topic đã được cập nhật thành công!',
                color: 'green',
            });
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.response?.data?.detail || 'Không thể cập nhật topic.',
                color: 'red',
            });
        }
    });

    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: async (topicId: number) => {
            return await deleteTopicAdmin(topicId);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'topics'] });
            setDeleteModalOpened(false);
            setSelectedTopic(null);
            notifications.show({
                title: 'Thành công',
                message: 'Topic đã được xóa thành công!',
                color: 'green',
            });
        },
        onError: (err: any) => {
            notifications.show({
                title: 'Lỗi',
                message: err.response?.data?.detail || 'Không thể xóa topic.',
                color: 'red',
            });
        }
    });

    const handleEdit = (topic: Topic) => {
        setSelectedTopic(topic);
        editForm.setValues({
            name: topic.name,
            description: topic.description || "",
            courseId: topic.courseId,
        });
        setEditModalOpened(true);
    };

    const handleDelete = (topic: Topic) => {
        setSelectedTopic(topic);
        setDeleteModalOpened(true);
    };

    const getCourseNameById = (courseId: number) => {
        const course = courses.find(c => c.id === courseId);
        return course?.title || `Course ${courseId}`;
    };

    const courseOptions = courses.map(course => ({
        value: course.id.toString(),
        label: course.title,
    }));

    return (
        <Container size="xl" className="py-8">
            <LoadingOverlay visible={loadingTopics} />

            {/* Header */}
            <Group justify="space-between" mb="xl">
                <div>
                    <Title order={2} className="text-gray-800">
                        Quản lý Topics
                    </Title>
                    <Text size="sm" c="dimmed">
                        Quản lý các chủ đề trong hệ thống
                    </Text>
                </div>
                <Button
                    leftSection={<IconPlus size={16} />}
                    onClick={() => setCreateModalOpened(true)}
                >
                    Tạo Topic mới
                </Button>
            </Group>

            {/* Search and Stats */}
            <Paper p="md" mb="lg">
                <Grid>
                    <Grid.Col span={{ base: 12, md: 6 }}>
                        <TextInput
                            placeholder="Tìm kiếm topic..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.currentTarget.value)}
                            leftSection={<IconSearch size={16} />}
                        />
                    </Grid.Col>
                    <Grid.Col span={{ base: 12, md: 6 }}>
                        <Group justify="flex-end">
                            <Badge size="lg" variant="light">
                                Tổng: {topics.length} topics
                            </Badge>
                        </Group>
                    </Grid.Col>
                </Grid>
            </Paper>

            {/* Topics Table */}
            <Paper shadow="sm">
                <Table highlightOnHover>
                    <Table.Thead>
                        <Table.Tr>
                            <Table.Th>Tên Topic</Table.Th>
                            <Table.Th>Mô tả</Table.Th>
                            <Table.Th>Khóa học</Table.Th>
                            <Table.Th>Ngày tạo</Table.Th>
                            <Table.Th width={100}>Thao tác</Table.Th>
                        </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                        {paginatedTopics.length === 0 ? (
                            <Table.Tr>
                                <Table.Td colSpan={5}>
                                    <Text ta="center" c="dimmed" py="xl">
                                        {searchQuery ? "Không tìm thấy topic nào" : "Chưa có topic nào"}
                                    </Text>
                                </Table.Td>
                            </Table.Tr>
                        ) : (
                            paginatedTopics.map((topic) => (
                                <Table.Tr key={topic.id}>
                                    <Table.Td>
                                        <Text fw={500}>{topic.name}</Text>
                                    </Table.Td>
                                    <Table.Td>
                                        <Text size="sm" c="dimmed" lineClamp={2}>
                                            {topic.description || "Không có mô tả"}
                                        </Text>
                                    </Table.Td>
                                    <Table.Td>
                                        <Badge variant="light" leftSection={<IconBook size={12} />}>
                                            {getCourseNameById(topic.courseId)}
                                        </Badge>
                                    </Table.Td>
                                    <Table.Td>
                                        <Text size="sm" c="dimmed">
                                            {new Date(topic.createdAt).toLocaleDateString('vi-VN')}
                                        </Text>
                                    </Table.Td>
                                    <Table.Td>
                                        <Menu shadow="md">
                                            <Menu.Target>
                                                <ActionIcon variant="subtle">
                                                    <IconDots size={16} />
                                                </ActionIcon>
                                            </Menu.Target>
                                            <Menu.Dropdown>
                                                <Menu.Item
                                                    leftSection={<IconEdit size={14} />}
                                                    onClick={() => handleEdit(topic)}
                                                >
                                                    Chỉnh sửa
                                                </Menu.Item>
                                                <Menu.Item
                                                    leftSection={<IconTrash size={14} />}
                                                    color="red"
                                                    onClick={() => handleDelete(topic)}
                                                >
                                                    Xóa
                                                </Menu.Item>
                                            </Menu.Dropdown>
                                        </Menu>
                                    </Table.Td>
                                </Table.Tr>
                            ))
                        )}
                    </Table.Tbody>
                </Table>

                {/* Pagination */}
                {totalPages > 1 && (
                    <Box p="md">
                        <Group justify="center">
                            <Pagination
                                value={page}
                                onChange={setPage}
                                total={totalPages}
                                size="sm"
                            />
                        </Group>
                    </Box>
                )}
            </Paper>

            {/* Create Modal */}
            <Modal
                opened={createModalOpened}
                onClose={() => {
                    setCreateModalOpened(false);
                    createForm.reset();
                }}
                title="Tạo Topic mới"
                size="md"
            >
                <form onSubmit={createForm.onSubmit((values) => createMutation.mutate(values))}>
                    <Grid>
                        <Grid.Col span={12}>
                            <TextInput
                                required
                                label="Tên Topic"
                                placeholder="Nhập tên topic..."
                                {...createForm.getInputProps("name")}
                            />
                        </Grid.Col>
                        <Grid.Col span={12}>
                            <Textarea
                                label="Mô tả"
                                placeholder="Mô tả topic..."
                                rows={3}
                                {...createForm.getInputProps("description")}
                            />
                        </Grid.Col>
                        <Grid.Col span={12}>
                            <Select
                                required
                                label="Khóa học"
                                placeholder="Chọn khóa học..."
                                data={courseOptions}
                                value={createForm.values.courseId?.toString()}
                                onChange={(value) => createForm.setFieldValue('courseId', value ? parseInt(value) : null)}
                                error={createForm.errors.courseId}
                            />
                        </Grid.Col>
                    </Grid>
                    <Group justify="flex-end" mt="md">
                        <Button
                            variant="outline"
                            onClick={() => {
                                setCreateModalOpened(false);
                                createForm.reset();
                            }}
                        >
                            Hủy
                        </Button>
                        <Button
                            type="submit"
                            loading={createMutation.isPending}
                        >
                            Tạo
                        </Button>
                    </Group>
                </form>
            </Modal>

            {/* Edit Modal */}
            <Modal
                opened={editModalOpened}
                onClose={() => {
                    setEditModalOpened(false);
                    setSelectedTopic(null);
                    editForm.reset();
                }}
                title="Chỉnh sửa Topic"
                size="md"
            >
                <form onSubmit={editForm.onSubmit((values) => updateMutation.mutate(values))}>
                    <Grid>
                        <Grid.Col span={12}>
                            <TextInput
                                required
                                label="Tên Topic"
                                placeholder="Nhập tên topic..."
                                {...editForm.getInputProps("name")}
                            />
                        </Grid.Col>
                        <Grid.Col span={12}>
                            <Textarea
                                label="Mô tả"
                                placeholder="Mô tả topic..."
                                rows={3}
                                {...editForm.getInputProps("description")}
                            />
                        </Grid.Col>
                        <Grid.Col span={12}>
                            <Select
                                label="Khóa học"
                                placeholder="Chọn khóa học..."
                                data={courseOptions}
                                value={editForm.values.courseId?.toString()}
                                onChange={(value) => editForm.setFieldValue('courseId', value ? parseInt(value) : null)}
                            />
                        </Grid.Col>
                    </Grid>
                    <Group justify="flex-end" mt="md">
                        <Button
                            variant="outline"
                            onClick={() => {
                                setEditModalOpened(false);
                                setSelectedTopic(null);
                                editForm.reset();
                            }}
                        >
                            Hủy
                        </Button>
                        <Button
                            type="submit"
                            loading={updateMutation.isPending}
                        >
                            Cập nhật
                        </Button>
                    </Group>
                </form>
            </Modal>

            {/* Delete Confirmation Modal */}
            <Modal
                opened={deleteModalOpened}
                onClose={() => {
                    setDeleteModalOpened(false);
                    setSelectedTopic(null);
                }}
                title="Xác nhận xóa"
                size="sm"
            >
                <Alert icon={<IconAlertCircle size="1rem" />} color="red" mb="md">
                    Bạn có chắc chắn muốn xóa topic "{selectedTopic?.name}"?
                    Hành động này không thể hoàn tác.
                </Alert>
                <Group justify="flex-end">
                    <Button
                        variant="outline"
                        onClick={() => {
                            setDeleteModalOpened(false);
                            setSelectedTopic(null);
                        }}
                    >
                        Hủy
                    </Button>
                    <Button
                        color="red"
                        loading={deleteMutation.isPending}
                        onClick={() => selectedTopic && deleteMutation.mutate(selectedTopic.id)}
                    >
                        Xóa
                    </Button>
                </Group>
            </Modal>
        </Container>
    );
} 