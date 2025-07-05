import { Metadata } from "next";
import CourseLearnClient from "./components/CourseLearnClient";

type Props = {
    params: Promise<{
        id: string;
    }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { id } = await params;
    return {
        title: `Học tập khóa học | AI Agent Giải Thuật`,
        description: "Lộ trình học tập khóa học với các chủ đề và bài học",
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["học tập", "khóa học", "giải thuật", "lập trình", "lộ trình"],
    };
}

export default async function CourseLearnPage({ params }: Props) {
    const { id } = await params;
    return <CourseLearnClient courseId={parseInt(id)} />;
} 