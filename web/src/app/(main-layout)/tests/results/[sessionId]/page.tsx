import React from 'react';
import { Metadata } from 'next';
import TestResultClient from './TestResultClient';

interface TestResultPageProps {
    params: Promise<{
        sessionId: string;
    }>;
}

export async function generateMetadata({ params }: TestResultPageProps): Promise<Metadata> {
    const { sessionId } = await params;
    return {
        title: `Kết quả bài kiểm tra ${sessionId} - AI Agent Giải Thuật`,
        description: `Xem chi tiết kết quả bài kiểm tra và phân tích hiệu suất học tập`,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["giải thuật", "học tập", "lập trình", "AI", "kết quả kiểm tra", "phân tích"],
    };
}

export default async function TestResultPage({ params }: TestResultPageProps) {
    const { sessionId } = await params;
    return <TestResultClient sessionId={sessionId} />;
}