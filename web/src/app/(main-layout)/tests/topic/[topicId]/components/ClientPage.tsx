'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { testApi } from '@/lib/api';
import { useAppSelector } from '@/lib/store';

interface ClientPageProps {
    topicId: number;
}

export default function ClientPage({ topicId }: ClientPageProps) {
    const router = useRouter();
    const userState = useAppSelector(state => state.user);

    useEffect(() => {
        const createTestSession = async () => {
            if (!userState.user) {
                router.push('/auth/login');
                return;
            }

            try {
                const tests = await testApi.getTestsByTopic(topicId);
                if (tests && tests.length > 0) {
                    const test = tests[0]; // Lấy test đầu tiên
                    const session = await testApi.createTestSession({
                        testId: test.id
                    });
                    console.log('Created session with UUID:', session.id);
                    router.push(`/tests/${session.id}`);
                } else {
                    console.error("No test found for topic:", topicId);
                    router.push('/tests'); // Redirect to tests list
                }
            } catch (error) {
                console.error("Error creating test session from topic:", error);
                router.push('/tests'); // Redirect to tests list on error
            }
        };

        if (userState.user) {
            createTestSession();
        }
    }, [userState.user, topicId, router]);

    return <div>Đang tạo phiên làm bài...</div>;
} 