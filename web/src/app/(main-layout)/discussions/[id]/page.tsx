import DiscussionDetailClient from "@/components/discussions/DiscussionDetailClient";
import { Metadata } from "next";

interface DiscussionDetailPageProps {
  params: Promise<{ id: string }>;
}

// Generate metadata
export async function generateMetadata({ params }: DiscussionDetailPageProps): Promise<Metadata> {
  const { id } = await params;
  return {
    title: `Discussion ${id} - AI Agent Giải Thuật`,
    description: `View discussion ${id} and participate in the conversation`,
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["discussion", "community", "conversation", "AI", "algorithms"],
  };
}

export default async function DiscussionDetailPage({ params }: DiscussionDetailPageProps) {
  const { id } = await params;

  if (!id || isNaN(Number(id))) {
    throw new Error("Invalid discussion ID");
  }

  const discussionId = Number(id);

  return <DiscussionDetailClient id={discussionId} />;
}
