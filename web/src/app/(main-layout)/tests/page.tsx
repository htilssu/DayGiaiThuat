import React, { Suspense } from 'react';
import { Metadata } from 'next';
import ClientPage from './components/ClientPage';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export const metadata: Metadata = {
    title: "Danh sách bài kiểm tra - AI Agent Giải Thuật",
    description: "Danh sách các bài kiểm tra trắc nghiệm và lập trình trên nền tảng học giải thuật thông minh",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "AI", "kiểm tra", "trắc nghiệm", "bài tập"],
};

export default function TestsPage() {
    return (
        <Suspense fallback={<LoadingSpinner />}>
            <ClientPage />
        </Suspense>
    );
} 