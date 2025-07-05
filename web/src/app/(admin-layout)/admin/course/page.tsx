import { Metadata } from "next";
import CourseAdminClient from "@/components/admin/course/CourseAdminClient";

export const metadata: Metadata = {
    title: "Quản lý Khóa học",
    description: "Trang quản lý các khóa học và chủ đề cho quản trị viên.",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["quản trị", "khóa học", "chủ đề", "admin"],
};

export default function AdminCoursePage() {
    return <CourseAdminClient />;
} 