import { testApi, TestHistorySummary } from '@/lib/api'
import { Badge, Button, Group, Stack, Table, Text } from '@mantine/core'
import React from 'react'
import { IconCalendar, IconCheck, IconClock, IconClockHour9, IconTarget, IconTrophy, IconX } from '@tabler/icons-react'
import { useRouter } from 'next/navigation'

export default function TestSessionHistoryRow({ session }: { session: TestHistorySummary }) {
    const router = useRouter();

    const handleStartTest = async (testId: number) => {
        router.push(`/tests/${session.sessionId}`);
    };

    const handleViewResult = (sessionId: string) => {
        router.push(`/tests/results/${sessionId}`);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'completed':
                return 'green';
            case 'expired':
                return 'orange';
            case 'in_progress':
                return 'blue';
            default:
                return 'gray';
        }
    };

    const getStatusLabel = (status: string, isSubmitted: boolean) => {
        if (status === 'completed' && isSubmitted) return 'Hoàn thành';
        if (status === 'expired') return 'Hết thời gian';
        if (status === 'in_progress') return 'Đang làm';
        return 'Chưa xác định';
    };

    const formatDuration = (minutes: number) => {
        if (minutes < 60) {
            return `${minutes} phút`;
        }
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return remainingMinutes > 0
            ? `${hours}h ${remainingMinutes}m`
            : `${hours} giờ`;
    };

    const formatDate = (dateString: string | null | undefined) => {
        if (!dateString) {
            return 'Chưa bắt đầu';
        }
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Thời gian không hợp lệ';
            }
            return date.toLocaleString('vi-VN', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return 'Thời gian không hợp lệ';
        }
    };

    const formatTestDuration = (minutes: number) => {
        if (minutes < 60) {
            return `${minutes} phút`;
        }
        const hours = Math.floor(minutes / 60);
        const remainingMinutes = minutes % 60;
        return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours} giờ`;
    };

    return (
        <Table.Tr key={session.sessionId}>
            <Table.Td>
                <Stack gap={2}>
                    <Text fw={500} size="sm">
                        {session.testName}
                    </Text>
                </Stack>
            </Table.Td>
            <Table.Td>
                <Badge
                    color={getStatusColor(session.status)}
                    variant="light"
                    leftSection={
                        session.status === 'completed' ? <IconCheck size={12} /> :
                            session.status === 'expired' ? <IconClockHour9 size={12} /> :
                                <IconX size={12} />
                    }
                >
                    {getStatusLabel(session.status, true)}
                </Badge>
            </Table.Td>
            <Table.Td>
                <Group gap="xs">
                    <IconClock size={14} color="gray" />
                    <Text size="sm">
                        {formatTestDuration(session.durationMinutes)}
                    </Text>
                </Group>
            </Table.Td>
            <Table.Td>
                {session.score !== null && session.score !== undefined ? (
                    <Group gap="xs">
                        <IconTrophy size={14} color="gold" />
                        <Text size="sm" fw={500} c={
                            session.score >= 80 ? 'green' :
                                session.score >= 60 ? 'orange' : 'red'
                        }>
                            {Math.round(session.score)}%
                        </Text>
                    </Group>
                ) : (
                    <Text size="sm" c="dimmed">-</Text>
                )}
            </Table.Td>
            <Table.Td>
                {session.correctAnswers !== null && session.correctAnswers !== undefined ? (
                    <Group gap="xs">
                        <IconTarget size={14} color="green" />
                        <Text size="sm">
                            {session.correctAnswers}/{session.totalQuestions}
                        </Text>
                    </Group>
                ) : (
                    <Text size="sm" c="dimmed">-</Text>
                )}
            </Table.Td>
            <Table.Td>
                <Group gap="xs">
                    <IconCalendar size={14} color="gray" />
                    <Text size="sm">
                        {formatDate(session.startTime)}
                    </Text>
                </Group>
            </Table.Td>
            {
                session.status === 'in_progress' ? (
                    <Table.Td>
                        <Button
                            size="xs"
                            variant="filled"
                            onClick={() => handleStartTest(session.testId)}
                        >
                            Tiếp tục làm
                        </Button>
                    </Table.Td>
                ) : session.status !== 'in_progress' && (
                    <Table.Td>
                        <Button
                            size="xs"
                            variant="light"
                            onClick={() => handleViewResult(session.sessionId)}
                        >
                            Xem kết quả
                        </Button>
                    </Table.Td>
                )
            }
        </Table.Tr>
    )
}
