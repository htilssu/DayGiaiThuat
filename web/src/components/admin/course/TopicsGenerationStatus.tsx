"use client";

import { Badge } from "@mantine/core";

interface TopicsGenerationStatusProps {
    status: string;
}

export default function TopicsGenerationStatus({ status }: TopicsGenerationStatusProps) {
    const getStatusConfig = (status: string) => {
        switch (status.toLowerCase()) {
            case 'completed':
            case 'success':
                return { color: 'green', label: 'Đã tạo Topics' };
            case 'in_progress':
            case 'generating':
                return { color: 'yellow', label: 'Đang tạo Topics' };
            case 'failed':
            case 'error':
                return { color: 'red', label: 'Lỗi tạo Topics' };
            case 'not_started':
            case 'pending':
            default:
                return { color: 'gray', label: 'Chưa tạo Topics' };
        }
    };

    const config = getStatusConfig(status);

    return (
        <Badge 
            variant="light" 
            color={config.color}
            size="sm"
        >
            {config.label}
        </Badge>
    );
}
