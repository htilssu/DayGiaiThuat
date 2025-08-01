import React from 'react';
import { Metadata } from 'next';
import TopicClient from '@/components/pages/topics/TopicPage';
import { topicsApi } from '@/lib/api';

interface TopicPageProps {
  params: Promise<{ topicId: string }>;
}


export async function generateMetadata({ params }: TopicPageProps): Promise<Metadata> {
  const { topicId } = await params;

  const topic = await topicsApi.getTopicById(Number(topicId));

  return {
    title: `${topic.name} - AI Agent Giải Thuật`,
    description: `Học ${topic.name.toLowerCase()} với các bài giảng, bài tập và kiểm tra tương tác`,
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "AI", topic.name.toLowerCase()],
  };
}

export default async function TopicPage({ params }: TopicPageProps) {
  const { topicId } = await params;
  return <TopicClient topicId={topicId} />;
} 
