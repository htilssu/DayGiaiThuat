import CourseReviewPageClient from "@/components/admin/course/CourseReviewPageClient";
import { Metadata } from "next";

interface CourseReviewPageProps {
    params: Promise<{
        id: string;
    }>;
}

// Tạo metadata động dựa trên thông tin review khóa học
export async function generateMetadata({ params }: CourseReviewPageProps): Promise<Metadata> {
    const { id } = await params;
    return {
        title: `Review khóa học ${id} - AI Agent Giải Thuật`,
        description: `Review và duyệt nội dung khóa học ${id} được tạo bởi AI`,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["review", "khóa học", "AI", "admin", "duyệt nội dung"],
    };
}

export default async function CourseReviewPage({ params }: CourseReviewPageProps) {
    const { id } = await params;
    return <CourseReviewPageClient courseId={id} />;
}
