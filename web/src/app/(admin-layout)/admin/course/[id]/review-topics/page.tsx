import ReviewTopicsPageClient from "@/components/admin/course/ReviewTopicsPageClient";
import { Metadata } from "next";

interface ReviewTopicsPageProps {
    params: Promise<{
        id: string;
    }>;
}

export async function generateMetadata({ params }: ReviewTopicsPageProps): Promise<Metadata> {
    const { id } = await params;
    return {
        title: `Review Topics - Khóa học ${id} - AI Agent Giải Thuật`,
        description: `Review và tạo topics cho khóa học ${id}`,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["review", "topics", "khóa học", "admin"],
    };
}

export default async function ReviewTopicsPage({ params }: ReviewTopicsPageProps) {
    const { id } = await params;
    return <ReviewTopicsPageClient courseId={id} />;
}
