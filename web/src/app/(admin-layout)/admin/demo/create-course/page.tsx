import CreateCourseDemo from "@/components/demo/CreateCourseDemo";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Demo: Tạo Khóa học với AI - AI Agent Giải Thuật",
    description: "Demo workflow mới cho việc tạo khóa học với AI tự động generate topics và skills",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["demo", "tạo khóa học", "AI", "topics", "skills"],
};

export default function CreateCourseDemoPage() {
    return <CreateCourseDemo />;
}
