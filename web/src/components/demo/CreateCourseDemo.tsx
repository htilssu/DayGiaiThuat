"use client";

import {
    Container,
    Title,
    Text,
    Alert,
    Stack,
    Group,
    Button,
    Badge,
} from "@mantine/core";
import { IconInfoCircle, IconRocket, IconCheck } from "@tabler/icons-react";
import { useState } from "react";
import CreateCourseModal from "@/components/admin/course/CreateCourseModal";

export default function CreateCourseDemo() {
    const [modalOpened, setModalOpened] = useState(false);

    return (
        <Container size="lg" py="xl">
            <Stack gap="xl">
                <div>
                    <Title order={1} className="text-primary mb-4">
                        🚀 Tạo Khóa học với AI
                    </Title>
                    <Text size="lg" c="dimmed">
                        Workflow mới cho việc tạo khóa học với tự động generate topics và skills
                    </Text>
                </div>

                <Alert 
                    icon={<IconInfoCircle size="1rem" />} 
                    title="Workflow mới"
                    color="blue"
                >
                    <Stack gap="sm">
                        <Text size="sm">
                            Từ giờ việc tạo khóa học sẽ có 2 bước chính:
                        </Text>
                        <Group gap="xs">
                            <Badge variant="filled" color="blue">1</Badge>
                            <Text size="sm">Nhập thông tin khóa học → Tạo khóa học cơ bản</Text>
                        </Group>
                        <Group gap="xs">
                            <Badge variant="filled" color="green">2</Badge>
                            <Text size="sm">Chuyển đến trang Review → AI tạo topics → Lưu vào database</Text>
                        </Group>
                        <Text size="sm" fw={500} className="text-primary">
                            ✅ Bạn có toàn quyền kiểm soát trước khi lưu!
                        </Text>
                    </Stack>
                </Alert>

                <Stack gap="md">
                    <Title order={3} className="text-accent">
                        📋 Cấu trúc Response mới:
                    </Title>
                    <Alert color="green">
                        <Stack gap="xs">
                            <Text size="sm" fw={500}>Mỗi topic bao gồm:</Text>
                            <Text size="sm">• Tên và mô tả topic</Text>
                            <Text size="sm">• Prerequisites (nếu có)</Text>
                            <Text size="sm">• Danh sách 3-7 skills cụ thể</Text>
                            <Text size="sm">• Thứ tự logic (order)</Text>
                            <Text size="sm">• Ước lượng thời gian hoàn thành</Text>
                        </Stack>
                    </Alert>
                </Stack>

                <Stack gap="md">
                    <Title order={3} className="text-accent">
                        🔄 Luồng hoạt động:
                    </Title>
                    <Group gap="md" align="stretch">
                        <Alert color="blue" style={{ flex: 1 }}>
                            <Stack gap="xs" align="center">
                                <IconRocket size={24} />
                                <Text size="sm" fw={500}>Step 1</Text>
                                <Text size="xs" ta="center">
                                    Tạo khóa học cơ bản (title, description, level...)
                                </Text>
                            </Stack>
                        </Alert>
                        <Alert color="yellow" style={{ flex: 1 }}>
                            <Stack gap="xs" align="center">
                                <IconInfoCircle size={24} />
                                <Text size="sm" fw={500}>Step 2</Text>
                                <Text size="xs" ta="center">
                                    Chuyển đến trang Review Topics
                                </Text>
                            </Stack>
                        </Alert>
                        <Alert color="green" style={{ flex: 1 }}>
                            <Stack gap="xs" align="center">
                                <IconCheck size={24} />
                                <Text size="sm" fw={500}>Step 3</Text>
                                <Text size="xs" ta="center">
                                    AI tạo topics → Review → Lưu database
                                </Text>
                            </Stack>
                        </Alert>
                    </Group>
                </Stack>

                <Group justify="center" mt="xl">
                    <Button 
                        size="lg"
                        leftSection={<IconRocket size={20} />}
                        onClick={() => setModalOpened(true)}
                        gradient={{ from: 'blue', to: 'green', deg: 45 }}
                        variant="gradient"
                    >
                        Thử Tạo Khóa học Mới
                    </Button>
                </Group>

                <CreateCourseModal
                    opened={modalOpened}
                    onClose={() => setModalOpened(false)}
                    onSuccess={() => {
                        console.log("Course created successfully!");
                    }}
                />
            </Stack>
        </Container>
    );
}
