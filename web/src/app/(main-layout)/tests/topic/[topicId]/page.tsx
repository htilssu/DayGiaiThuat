import React from 'react';
import { Metadata } from 'next';
import ClientPage from './components/ClientPage';

export const metadata: Metadata = {
    title: "Bài kiểm tra theo chủ đề - AI Agent Giải Thuật",
    description: "Làm bài kiểm tra theo chủ đề cụ thể để đánh giá kiến thức",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "AI", "kiểm tra", "chủ đề"],
};

interface PageProps {
    params: Promise<{ topicId: string }>;
}

export default async function TopicTestPage({ params }: PageProps) {
    const { topicId } = await params;
    return <ClientPage topicId={parseInt(topicId)} />;
}  