import { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "../globals.css";
import Navbar from "@/components/ui/Navbar";
import Footer from "@/components/ui/Footer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

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
      className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col bg-background text-foreground transition-theme`}
    >
      <Navbar />
      <main className="flex-grow container mx-auto px-4 sm:px-6 py-8 md:py-12">
        {children}
      </main>
      <Footer />
    </div>
  );
}
