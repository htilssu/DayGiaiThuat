import React from 'react';
import { Metadata } from 'next';
import ClientPage from './components/ClientPage';

export const metadata: Metadata = {
    title: "Làm bài kiểm tra - AI Agent Giải Thuật",
    description: "Tham gia bài kiểm tra kiến thức giải thuật với hệ thống chấm điểm tự động",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "AI", "kiểm tra", "bài tập"],
};

export default function TestSessionPage() {
    return <ClientPage />;
} 