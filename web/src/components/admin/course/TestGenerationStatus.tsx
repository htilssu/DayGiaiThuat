'use client';

import React from 'react';
import { Badge, Group, Text, Button, Loader, Alert } from '@mantine/core';
import { IconCheck, IconX, IconClock, IconReload, IconAlertTriangle } from '@tabler/icons-react';

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
                return 'Hệ thống đang tự động tạo bài kiểm tra đầu vào cho khóa học này. Quá trình có thể mất vài phút...';
            case 'success':
                return 'Bài kiểm tra đầu vào đã được tạo thành công. Học viên có thể làm bài test.';
            case 'failed':
                return 'Có lỗi xảy ra khi tạo bài test. Có thể do dịch vụ AI tạm thời không khả dụng.';
            case 'not_started':
            default:
                return 'Bài kiểm tra đầu vào chưa được tạo cho khóa học này.';
        }
    };

    const showGenerateButton = () => {
        return (status === 'not_started' || status === 'failed') && !loading;
    };

    const getButtonText = () => {
        if (loading) return 'Đang tạo...';
        return status === 'failed' ? 'Tạo lại test' : 'Tạo test';
    };

    return (
        <div className="space-y-3">
            <Group justify="space-between" align="flex-start">
                <div className="space-y-2 flex-1">
                    <Group>
                        <Text size="sm" fw={500}>
                            Trạng thái:
                        </Text>
                        {getStatusBadge()}
                    </Group>

                    <Text size="sm" c="dimmed">
                        {getDescription()}
                    </Text>

                    {/* Show additional info for failed status */}
                    {status === 'failed' && (
                        <Alert
                            icon={<IconAlertTriangle size={16} />}
                            color="orange"
                            variant="light"
                        >
                            <Text size="xs">
                                Lỗi thường xảy ra do dịch vụ AI tạm thời quá tải. Vui lòng thử lại sau vài phút.
                            </Text>
                        </Alert>
                    )}

                    {/* Show additional info for pending status */}
                    {status === 'pending' && (
                        <Alert
                            icon={<Loader size={16} />}
                            color="blue"
                            variant="light"
                        >
                            <Text size="xs">
                                Không đóng trang này. Quá trình tạo test có thể mất 2-5 phút.
                            </Text>
                        </Alert>
                    )}
                </div>

                {showGenerateButton() && onGenerateTest && (
                    <Button
                        size="xs"
                        variant={status === 'failed' ? 'filled' : 'outline'}
                        color={status === 'failed' ? 'orange' : 'blue'}
                        leftSection={<IconReload size={14} />}
                        onClick={onGenerateTest}
                        loading={loading}
                    >
                        {getButtonText()}
                    </Button>
                )}
            </Group>
        </div>
    );
} 