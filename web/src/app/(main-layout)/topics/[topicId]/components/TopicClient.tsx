'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button, Loader, Alert } from '@mantine/core';
import { IconAlertCircle, IconExternalLink } from '@tabler/icons-react';
import { testApi, Test } from '@/lib/api';

interface TopicClientProps {
    topicId: string;
    topic: {
        title: string;
        description: string;
        color: string;
        icon: string;
    };
    lessons: {
        id: string;
        title: string;
        description: string;
    }[];
}

const TopicClient: React.FC<TopicClientProps> = ({ topicId, topic, lessons }) => {
    const router = useRouter();
    const [test, setTest] = useState<Test | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchTopicTest = async () => {
            try {
                setLoading(true);
                const topicTest = await testApi.getTestByTopic(topicId);
                setTest(topicTest);
            } catch (err) {
                console.error('Error fetching topic test:', err);
                setError('Không thể tải bài kiểm tra cho chủ đề này.');
            } finally {
                setLoading(false);
            }
        };

        fetchTopicTest();
    }, [topicId]);

    const handleStartTest = () => {
        if (test) {
            router.push(`/tests/${test.id}`);
        }
    };

    return (
        <div className="min-h-screen pb-20">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-10">
                    <Link href="/learn" className="text-primary hover:underline mb-2 inline-block">
                        ← Quay lại lộ trình
                    </Link>
                    <div className="flex items-center gap-4 mb-4">
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center bg-${topic.color} text-white text-2xl`}>
                            {topic.icon}
                        </div>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold">{topic.title}</h1>
                            <p className="text-foreground/70">{topic.description}</p>
                        </div>
                    </div>
                </div>

                {/* Danh sách bài học */}
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-2xl font-bold mb-6">Các bài học trong chủ đề này</h2>

                    <div className="space-y-4">
                        {lessons.length > 0 ? (
                            lessons.map((lesson) => (
                                <Link
                                    key={lesson.id}
                                    href={`/topics/${topicId}/lessons/${lesson.id}`}
                                    className="block bg-white rounded-xl p-6 shadow-sm border border-foreground/10 hover:shadow-md transition-all"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center bg-${topic.color} text-white font-bold`}>
                                            {lesson.id}
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-semibold">{lesson.title}</h3>
                                            <p className="text-foreground/70">{lesson.description}</p>
                                        </div>
                                    </div>
                                </Link>
                            ))
                        ) : (
                            <div className="text-center py-10 bg-foreground/5 rounded-lg">
                                <p className="text-foreground/70">Chưa có bài học nào trong chủ đề này</p>
                            </div>
                        )}
                    </div>

                    {/* Phần bài kiểm tra */}
                    <div className="mt-12 p-6 bg-primary/5 rounded-xl border border-primary/20">
                        <h2 className="text-2xl font-bold mb-4">Bài kiểm tra chủ đề</h2>
                        <p className="mb-6">Hoàn thành bài kiểm tra để mở khóa chủ đề tiếp theo trong lộ trình học tập.</p>

                        {loading ? (
                            <div className="flex items-center gap-2">
                                <Loader size="sm" />
                                <span>Đang tải bài kiểm tra...</span>
                            </div>
                        ) : error ? (
                            <Alert icon={<IconAlertCircle size="1rem" />} title="Lỗi" color="red">
                                {error}
                            </Alert>
                        ) : test ? (
                            <div>
                                <div className="mb-4">
                                    <h3 className="text-xl font-semibold">{test.title}</h3>
                                    <p className="text-foreground/70">{test.description}</p>
                                    <p className="mt-2">
                                        <span className="font-medium">Thời gian:</span> {test.duration} phút
                                    </p>
                                    <p>
                                        <span className="font-medium">Số câu hỏi:</span> {test.questions.length} câu
                                    </p>
                                </div>
                                <Button
                                    onClick={handleStartTest}
                                    rightSection={<IconExternalLink size="1rem" />}
                                    size="md"
                                >
                                    Bắt đầu làm bài kiểm tra
                                </Button>
                            </div>
                        ) : (
                            <div className="text-center py-6">
                                <p className="text-foreground/70">Chưa có bài kiểm tra nào cho chủ đề này</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TopicClient; 