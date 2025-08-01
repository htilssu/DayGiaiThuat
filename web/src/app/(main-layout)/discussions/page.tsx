import { Metadata } from 'next';
import { Suspense } from 'react';
import DiscussionsClient from '@/components/discussions/DiscussionsClient';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export const metadata: Metadata = {
  title: "Discussions - AI Agent Giải Thuật",
  description: "Tham gia thảo luận về các chủ đề giải thuật, chia sẻ kinh nghiệm và học hỏi từ cộng đồng",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["thảo luận", "giải thuật", "cộng đồng", "học tập", "AI"],
};

export default function DiscussionsPage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <DiscussionsClient />
    </Suspense>
  );
}
