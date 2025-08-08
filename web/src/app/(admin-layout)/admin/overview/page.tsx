import { Metadata } from "next";
import Overview from "@/components/admin/Overview";

export const metadata: Metadata = {
  title: "Tổng quan - Admin Dashboard",
  description: "Tổng quan thống kê và báo cáo hệ thống",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["admin", "dashboard", "tổng quan", "thống kê", "báo cáo"],
};

export default function OverviewPage() {
  return <Overview />;
}
