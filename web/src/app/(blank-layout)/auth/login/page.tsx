import { Metadata } from "next";
import { Suspense } from "react";
import LoginClient from "@/components/auth/LoginClient";
import LoadingSpinner from "@/components/ui/LoadingSpinner";

export const metadata: Metadata = {
  title: "Đăng nhập | AI Giải Thuật",
  description: "Đăng nhập để tiếp tục hành trình khám phá và chinh phục thế giới thuật toán cùng cộng đồng học tập.",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["đăng nhập", "tài khoản", "giải thuật", "học tập", "AI"],
};

export default function LoginPage() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <LoginClient />
    </Suspense>
  );
}
