import React from 'react';
import { Metadata } from 'next';
import TopicClient from './components/TopicClient';

interface TopicPageProps {
    params: Promise<{ topicId: string }>;
}

// Sample data - should be replaced with API calls
const getTopicData = async (topicId: string) => {
    // In real implementation, fetch from your API
    return {
        id: parseInt(topicId),
        name: `Topic ${topicId}`,
        description: `Description for topic ${topicId}`,
        lessons: [],
        exercises: [],
        tests: []
    };
};

// Danh sách các topic mẫu cho metadata
const topicTitles: Record<string, string> = {
    '1': 'Cấu trúc dữ liệu cơ bản',
    '2': 'Thuật toán sắp xếp',
    '3': 'Thuật toán tìm kiếm',
    '4': 'Đệ quy và quay lui',
    '5': 'Quy hoạch động',
    '6': 'Cây và đồ thị',
    '7': 'Thuật toán tham lam',
    '8': 'Xử lý chuỗi'
};

export async function generateMetadata({ params }: TopicPageProps): Promise<Metadata> {
    const { topicId } = await params;
    const topicTitle = topicTitles[topicId] || `Chủ đề ${topicId}`;

    return {
        title: `${topicTitle} - AI Agent Giải Thuật`,
        description: `Học ${topicTitle.toLowerCase()} với các bài giảng, bài tập và kiểm tra tương tác`,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["giải thuật", "học tập", "lập trình", "AI", topicTitle.toLowerCase()],
    };
}

export default async function TopicPage({ params }: TopicPageProps) {
    const { topicId } = await params;
    return <TopicClient topicId={topicId} />;
} 