import React from 'react';
import { Metadata } from 'next';
import EntryTestConfirmClient from './EntryTestConfirmClient';

export const metadata: Metadata = {
    title: "Xác nhận làm bài test đầu vào - AI Agent Giải Thuật",
    description: "Xác nhận trước khi bắt đầu làm bài kiểm tra đầu vào khóa học",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "AI", "kiểm tra", "test đầu vào"],
};

interface PageProps {
    params: Promise<{ courseId: string }>;
}

export default async function EntryTestConfirmPage({ params }: PageProps) {
    const { courseId } = await params;
    return <EntryTestConfirmClient courseId={courseId} />;
} 