'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { testApi } from '@/lib/api';
import { useAppSelector } from '@/lib/store';

export default function TopicTestPage({ params }: { params: { topicId: string } }) {
    const router = useRouter();
    const userState = useAppSelector(state => state.user);

    useEffect(() => {
        const createTestSession = async () => {
            if (!userState.user) {
                router.push('/auth/login');
                return;
            }

            try {
                const test = await testApi.getTestByTopic(params.topicId);
                if (test) {
                    const session = await testApi.createTestSession({
                        user_id: userState.user.id,
                        test_id: parseInt(test.id)
                    });
                    console.log('Created session with UUID:', session.id);
                    router.push(`/tests/${session.id}`);
                } else {
                    console.error("No test found for topic:", params.topicId);
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
    }, [userState.user, params.topicId, router]);

    return <div>Đang tạo phiên làm bài...</div>;
}  