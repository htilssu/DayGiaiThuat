import { Metadata } from "next";
import { LessonPage } from "@/components/pages/learn/LessonPage";
import { getLesson } from "@/components/pages/learn/sampleLessonData";
import { notFound } from "next/navigation";

interface LessonPageProps {
    params: {
        topicId: string;
        lessonId: string;
    };
}

// Tạo metadata động dựa trên thông tin bài học
export async function generateMetadata({ params }: LessonPageProps): Promise<Metadata> {
    const { topicId, lessonId } = params;
    const lesson = getLesson(topicId, lessonId);

    if (!lesson) {
        return {
            title: "Không tìm thấy bài học | AI Agent Giải Thuật",
            description: "Bài học không tồn tại hoặc đã bị xóa",
        };
    }

    return {
        title: `${lesson.title} | ${lesson.topicTitle} | AI Agent Giải Thuật`,
        description: lesson.description,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["giải thuật", "học tập", "lập trình", "bài học", lesson.topicTitle, lesson.title],
    };
}

export default function LessonPageRoute({ params }: LessonPageProps) {
    const { topicId, lessonId } = params;
    const lesson = getLesson(topicId, lessonId);

    if (!lesson) {
        notFound();
    }

    return <LessonPage lesson={lesson} />;
} 