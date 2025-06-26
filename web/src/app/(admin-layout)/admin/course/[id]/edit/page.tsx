import type { Metadata } from "next";
import EditCourseClient from "./EditCourseClient";

export const metadata: Metadata = {
    title: "Chỉnh sửa khóa học - Admin Dashboard",
    description: "Trang chỉnh sửa thông tin khóa học cho quản trị viên",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["admin", "chỉnh sửa", "khóa học", "quản lý"],
};

interface EditCoursePageProps {
    params: Promise<{
        id: string;
    }>;
}

export default async function EditCoursePage({ params }: EditCoursePageProps) {
    const resolvedParams = await params;
    return <EditCourseClient courseId={parseInt(resolvedParams.id)} />;
} 