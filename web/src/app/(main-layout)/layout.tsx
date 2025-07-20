import { Metadata } from "next";
import "../globals.css";
import Navbar from "@/components/ui/Navbar";
import Footer from "@/components/ui/Footer";
import { Suspense } from "react";
import LoadingSpinner from "@/components/ui/LoadingSpinner";


export const metadata: Metadata = {
  title: "Ứng dụng học giải thuật thông minh",
  description: "Nền tảng học giải thuật thông minh với AI Assistant",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["giải thuật", "học tập", "lập trình", "AI", "bài tập"],
};

export default function MainLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div
      className={`antialiased min-h-screen flex flex-col bg-background text-foreground transition-theme`}>
      <Navbar />
      <main className="flex-grow container mx-auto px-4 sm:px-6 py-8 md:py-12">
        {children}
      </main>
      <Suspense fallback={<div className="flex justify-center items-center h-64"><LoadingSpinner /></div>}>
        <Footer />
      </Suspense>
    </div>
  );
}
