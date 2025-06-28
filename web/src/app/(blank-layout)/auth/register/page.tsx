import { Metadata } from "next";
import RegisterClient from "@/components/auth/RegisterClient";

export const metadata: Metadata = {
  title: "Đăng ký tài khoản | AI Giải Thuật",
  description: "Tạo tài khoản để khám phá và học tập cùng hệ thống giải thuật thông minh tiên tiến nhất hiện nay.",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["đăng ký", "tài khoản", "giải thuật", "học tập", "AI"],
};

export default function RegisterPage() {
  return <RegisterClient />;
}
