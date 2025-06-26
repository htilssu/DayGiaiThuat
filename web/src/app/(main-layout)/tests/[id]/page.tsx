import React from 'react';
import { Metadata } from 'next';
import ClientPage from './components/ClientPage';

export const metadata: Metadata = {
    title: "Làm bài kiểm tra - AI Agent Giải Thuật",
    description: "Làm bài kiểm tra trắc nghiệm và lập trình trên nền tảng học giải thuật thông minh",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "AI", "kiểm tra", "trắc nghiệm", "bài tập"],
};

export default function TestPage({ params }: { params: { id: string } }) {
    return <ClientPage sessionId={params.id} />;
} 