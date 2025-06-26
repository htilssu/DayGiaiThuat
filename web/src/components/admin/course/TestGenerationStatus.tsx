'use client';

import React from 'react';
import { Badge, Group, Text, Button, Loader } from '@mantine/core';
import { IconCheck, IconX, IconClock, IconReload } from '@tabler/icons-react';

interface TestGenerationStatusProps {
    status: string;
    onGenerateTest?: () => void;
    loading?: boolean;
}

export default function TestGenerationStatus({
    status,
    onGenerateTest,
    loading = false
}: TestGenerationStatusProps) {
    const getStatusBadge = () => {
        switch (status) {
            case 'pending':
                return (
                    <Badge
                        color="yellow"
                        variant="light"
                        leftSection={<Loader size="xs" />}
                    >
                        Đang tạo test
                    </Badge>
                );
            case 'success':
                return (
                    <Badge
                        color="green"
                        variant="light"
                        leftSection={<IconCheck size={12} />}
                    >
                        Đã tạo test thành công
                    </Badge>
                );
            case 'failed':
                return (
                    <Badge
                        color="red"
                        variant="light"
                        leftSection={<IconX size={12} />}
                    >
                        Tạo test thất bại
                    </Badge>
                );
            case 'not_started':
            default:
                return (
                    <Badge
                        color="gray"
                        variant="light"
                        leftSection={<IconClock size={12} />}
                    >
                        Chưa tạo test
                    </Badge>
                );
        }
    };

    const getDescription = () => {
        switch (status) {
            case 'pending':
                return 'Hệ thống đang tự động tạo bài kiểm tra đầu vào cho khóa học này...';
            case 'success':
                return 'Bài kiểm tra đầu vào đã được tạo thành công. Học viên có thể làm bài test.';
            case 'failed':
                return 'Có lỗi xảy ra khi tạo bài test. Vui lòng thử tạo lại.';
            case 'not_started':
            default:
                return 'Bài kiểm tra đầu vào chưa được tạo cho khóa học này.';
        }
    };

    const showGenerateButton = () => {
        return (status === 'not_started' || status === 'failed') && !loading;
    };

    return (
        <div className="space-y-3">
            <Group justify="space-between" align="flex-start">
                <div className="space-y-2">
                    <Group>
                        <Text size="sm" fw={500}>
                            Trạng thái bài kiểm tra đầu vào:
                        </Text>
                        {getStatusBadge()}
                    </Group>

                    <Text size="sm" c="dimmed">
                        {getDescription()}
                    </Text>
                </div>

                {showGenerateButton() && onGenerateTest && (
                    <Button
                        size="xs"
                        variant="outline"
                        leftSection={<IconReload size={14} />}
                        onClick={onGenerateTest}
                        loading={loading}
                    >
                        {status === 'failed' ? 'Tạo lại test' : 'Tạo test'}
                    </Button>
                )}
            </Group>
        </div>
    );
} 