'use client';

import React, { useState, useEffect } from 'react';
import { Container, Title, Text, Stack, Card, Group, Button, Loader, Alert } from '@mantine/core';
import { IconAlertCircle, IconClock } from '@tabler/icons-react';
import { useRouter } from 'next/navigation';
import { Test, testApi } from '@/lib/api';

const ClientPage: React.FC = () => {
    const router = useRouter();
    const [tests, setTests] = useState<Test[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTests = async () => {
            try {
                setLoading(true);
                // Sử dụng testApi.getTests để lấy danh sách bài kiểm tra
                try {
                    const data = await testApi.getTests();
                    setTests(data);
                } catch (apiError) {
                    console.error('API error, using sample data:', apiError);
                    // Nếu API chưa sẵn sàng, sử dụng dữ liệu mẫu
                    const sampleData: Test[] = [
                        {
                            id: '1',
                            title: 'Kiểm tra giải thuật cơ bản',
                            description: 'Bài kiểm tra về các giải thuật sắp xếp, tìm kiếm và cấu trúc dữ liệu cơ bản',
                            duration: 60,
                            questions: []
                        },
                        {
                            id: '2',
                            title: 'Kiểm tra lập trình Python',
                            description: 'Bài kiểm tra về ngôn ngữ lập trình Python và các thư viện phổ biến',
                            duration: 90,
                            questions: []
                        },
                        {
                            id: '3',
                            title: 'Kiểm tra giải thuật nâng cao',
                            description: 'Bài kiểm tra về các giải thuật nâng cao như quy hoạch động, thuật toán tham lam',
                            duration: 120,
                            questions: []
                        }
                    ];
                    setTests(sampleData);
                }
            } catch (err) {
                console.error('Error fetching tests:', err);
                setError('Không thể tải danh sách bài kiểm tra. Vui lòng thử lại sau.');
            } finally {
                setLoading(false);
            }
        };

        fetchTests();
    }, []);

    const handleStartTest = (testId: string) => {
        router.push(`/tests/${testId}`);
    };

    if (loading) {
        return (
            <Container size="md" py="xl">
                <Stack align="center" justify="center" h={400}>
                    <Loader size="lg" />
                    <Text>Đang tải danh sách bài kiểm tra...</Text>
                </Stack>
            </Container>
        );
    }

    if (error) {
        return (
            <Container size="md" py="xl">
                <Alert icon={<IconAlertCircle size="1rem" />} title="Lỗi" color="red">
                    {error}
                </Alert>
            </Container>
        );
    }

    return (
        <Container size="md" py="xl">
            <Stack>
                <Title order={1}>Danh sách bài kiểm tra</Title>
                <Text color="dimmed">Chọn một bài kiểm tra để bắt đầu</Text>

                {tests.map((test) => (
                    <Card key={test.id} withBorder shadow="sm" p="md">
                        <Stack>
                            <Title order={3}>{test.title}</Title>
                            <Text>{test.description}</Text>

                            <Group>
                                <IconClock size="1rem" />
                                <Text>{test.duration} phút</Text>
                            </Group>

                            <Button onClick={() => handleStartTest(test.id)}>
                                Bắt đầu làm bài
                            </Button>
                        </Stack>
                    </Card>
                ))}
            </Stack>
        </Container>
    );
};

export default ClientPage; 