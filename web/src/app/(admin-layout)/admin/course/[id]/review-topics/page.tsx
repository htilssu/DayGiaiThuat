import CourseTopicsReviewPageClient from "@/components/admin/course/CourseTopicsReviewPageClient";
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
        description: `Review và chỉnh sửa topics cho khóa học ${id}`,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["review", "topics", "khóa học", "admin", "drag drop", "edit"],
    };
}

export default async function ReviewTopicsPage({ params }: ReviewTopicsPageProps) {
    const { id } = await params;
    return <CourseTopicsReviewPageClient courseId={id} />;
}
