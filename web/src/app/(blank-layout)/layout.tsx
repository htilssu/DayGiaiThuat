import { Metadata } from "next";
import { Analytics } from '@vercel/analytics/next';
import "../globals.css";


export const metadata: Metadata = {
  title: "Đăng nhập/Đăng ký - AI Agent Giải Thuật",
  description: "Đăng nhập hoặc đăng ký tài khoản để bắt đầu học giải thuật",
};

/**
 * Layout trang đăng nhập và đăng ký
 * @param {Object} props - Thuộc tính của component
 * @param {React.ReactNode} props.children - Các component con
 */
export default function BlankLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div
      className={`antialiased min-h-screen flex flex-col theme-transition bg-background text-foreground`}
    >
      {children}
      <Analytics />
    </div>
  );
}
