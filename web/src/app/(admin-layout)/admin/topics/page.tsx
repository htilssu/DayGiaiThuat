import { Metadata } from "next";
import TopicAdminClient from "@/components/admin/topics/TopicAdminClient";

export const metadata: Metadata = {
    title: "Quản lý Topics - Admin",
    description: "Quản lý các chủ đề trong hệ thống học giải thuật",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["admin", "topics", "quản lý", "chủ đề", "giải thuật"],
};

export default function AdminTopicsPage() {
    return <TopicAdminClient />;
} 