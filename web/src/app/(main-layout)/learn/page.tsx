import { Metadata } from "next";
import LearnClient from "./components/LearnClient";

export const metadata: Metadata = {
  title: "Học tập | AI Agent Giải Thuật",
  description: "Trang học tập cá nhân với danh sách các khóa học đã đăng ký",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["học tập", "khóa học", "giải thuật", "lập trình"],
};

export default function LearnPage() {
  return <LearnClient />;
}
