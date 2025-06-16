import { Metadata } from 'next'
import { LearnPage } from '@/components/pages/learn/LearnPage'

export const metadata: Metadata = {
    title: "Lộ trình học tập | AI Agent Giải Thuật",
    description: "Khám phá lộ trình học tập được thiết kế để giúp bạn làm chủ các giải thuật từ cơ bản đến nâng cao",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "lộ trình", "AI"],
}

export default function LearnPageRoute() {
    return <LearnPage />
}