import { Metadata } from 'next';

type Props = {
    params: Promise<{
        id: string;
    }>;
};

export const metadata: Metadata = {
    title: "Thảo luận - AI Agent Giải Thuật",
    description: "Tham gia thảo luận về các chủ đề học tập",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["thảo luận", "học tập", "lập trình", "AI", "bài tập"],
};

export default async function DiscussionPage({ params }: Props) {
    const { id } = await params;

    return (
        <div className="container mx-auto py-8">
            <h1 className="text-2xl font-bold mb-4">Thảo luận #{id}</h1>
            <p className="text-gray-600">Tính năng thảo luận đang được phát triển...</p>
        </div>
    );
}
