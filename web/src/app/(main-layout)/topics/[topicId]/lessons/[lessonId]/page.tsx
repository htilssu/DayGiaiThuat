import { Metadata } from "next";
import { LessonPage } from "@/components/pages/learn/LessonPage";
import { notFound } from "next/navigation";

interface LessonPageProps {
    params: Promise<{
        topicId: string;
        lessonId: string;
    }>;
}

// Tạo metadata động dựa trên thông tin bài học
export async function generateMetadata({ params }: LessonPageProps): Promise<Metadata> {
    const { lessonId } = await params;
    return {
        title: `Bài học ${lessonId} - AI Agent Giải Thuật`,
        description: `Học bài học ${lessonId} về giải thuật và lập trình`,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["giải thuật", "học tập", "lập trình", "AI", "bài học"],
    };
}

// Temporary lesson data - thay thế bằng API call thực tế
const getLessonData = (lessonId: string) => {
    return {
        id: lessonId,
        title: `Bài học ${lessonId}`,
        content: `Nội dung của bài học ${lessonId}`,
        duration: 30,
        completed: false
    };
};

export default async function LessonPageRoute({ params }: LessonPageProps) {
    const { lessonId, topicId } = await params;

    // Trong thực tế, bạn sẽ fetch data từ API
    const lesson = getLessonData(lessonId);

    if (!lesson) {
        notFound();
    }

    return <LessonPage lesson={lesson} />;
} 