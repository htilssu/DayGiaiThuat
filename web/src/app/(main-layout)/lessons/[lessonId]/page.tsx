import { LessonPage } from "@/components/pages/learn/LessonPage";
import { Metadata } from "next";

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


export default async function LessonPageRoute({ params }: LessonPageProps) {
    const { lessonId, topicId } = await params;
    // LessonPage sẽ tự fetch dữ liệu từ API
    return <LessonPage topicId={topicId} lessonId={lessonId} />;
}