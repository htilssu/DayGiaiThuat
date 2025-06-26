import type { Metadata } from "next";
import EditCourseClient from "./EditCourseClient";

export const metadata: Metadata = {
    title: "Chỉnh sửa khóa học - Admin Dashboard",
    description: "Trang chỉnh sửa thông tin khóa học cho quản trị viên",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["admin", "chỉnh sửa", "khóa học", "quản lý"],
};

interface EditCoursePageProps {
    params: {
        id: string;
    };
}

export default function EditCoursePage({ params }: EditCoursePageProps) {
    return <EditCourseClient courseId={parseInt(params.id)} />;
} 