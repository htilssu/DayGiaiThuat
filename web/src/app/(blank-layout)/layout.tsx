import { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

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
      className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col theme-transition bg-background text-foreground`}
    >
      {children}
    </div>
  );
}
