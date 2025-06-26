import { Metadata } from "next";
import CourseLearnClient from "./components/CourseLearnClient";

type Props = {
    params: {
        id: string;
    };
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    return {
        title: `Học tập khóa học | AI Agent Giải Thuật`,
        description: "Lộ trình học tập khóa học với các chủ đề và bài học",
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["học tập", "khóa học", "giải thuật", "lập trình", "lộ trình"],
    };
}

export default function CourseLearnPage({ params }: Props) {
    return <CourseLearnClient courseId={parseInt(params.id)} />;
} 