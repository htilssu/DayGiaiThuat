import { Metadata } from "next";
import { notFound } from "next/navigation";
import TopicPage from "@/components/pages/topics/TopicPage";

interface TopicPageProps {
  params: {
    topicId: string;
  };
}

// Tạo metadata động dựa trên thông tin chủ đề
export async function generateMetadata({
  params,
}: TopicPageProps): Promise<Metadata> {
  const { topicId } = params;

  return {
    title: `Chủ đề ${topicId} | AI Agent Giải Thuật`,
    description: "Tìm hiểu về các chủ đề giải thuật và lập trình",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["giải thuật", "học tập", "lập trình", "chủ đề"],
  };
}

export default function TopicPageWrapper({ params }: TopicPageProps) {
  const { topicId } = params;

  // Validate topicId is a number
  if (isNaN(parseInt(topicId))) {
    notFound();
  }

  return <TopicPage topicId={topicId} />;
}
