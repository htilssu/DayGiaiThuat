import { redirect } from 'next/navigation';
import { Metadata } from 'next';
import { testApi } from '@/lib/api';
import { getAuthHeaders } from '@/lib/utils/auth';

export const metadata: Metadata = {
    title: "Bài kiểm tra đầu vào - AI Agent Giải Thuật",
    description: "Làm bài kiểm tra đầu vào để đánh giá trình độ và nhận lộ trình học phù hợp",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "AI", "kiểm tra đầu vào", "đánh giá trình độ"],
};

export default async function TopicTestPage({ params }: { params: { topicId: string } }) {
    const headers = getAuthHeaders();
    if (!headers) {
        redirect('/auth/login');
    }

    try {
        const session = await testApi.createTestSessionFromTopic(parseInt(params.topicId), headers);
        redirect(`/tests/${session.id}`);
    } catch (error) {
        console.error("Error creating test session from topic:", error);
        // Handle error, maybe redirect to an error page or show a message
        redirect('/error'); // Or a more specific error page
    }
}  