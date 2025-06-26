import { Container, Title, Button, Alert } from "@mantine/core";
import { IconAlertCircle, IconArrowLeft } from "@tabler/icons-react";
import Link from "next/link";

export default function NotFound() {
    return (
        <Container size="xl" className="py-16 text-center">
            <Alert
                icon={<IconAlertCircle size="2rem" />}
                color="yellow"
                className="mb-8 max-w-md mx-auto"
            >
                <Title order={2} className="mb-2">Không tìm thấy khóa học</Title>
                <p>Khóa học bạn đang tìm có thể đã bị xóa hoặc không tồn tại.</p>
            </Alert>

            <Button
                component={Link}
                href="/admin/course"
                leftSection={<IconArrowLeft size={16} />}
                size="lg"
                className="bg-primary hover:bg-primary/90"
            >
                Quay lại danh sách khóa học
            </Button>
        </Container>
    );
} 