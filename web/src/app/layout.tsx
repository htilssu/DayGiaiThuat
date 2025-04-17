import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/contexts/ThemeContext";
import ThemeInitializer from "../components/ThemeInitializer";
import HeadScripts from "./head-scripts";
import { AuthProvider } from "@/contexts/AuthContext";
import { cn } from "@/lib/utils";
import "@mantine/core/styles.css";
import { MantineThemeProvider } from "@/components/MantineThemeProvider";

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

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0f172a" },
  ],
};

/**
 * Layout gốc của ứng dụng
 * @param {Object} props - Thuộc tính của component
 * @param {React.ReactNode} props.children - Các component con
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <HeadScripts />
      </head>
      <body
        suppressHydrationWarning
        className={`${geistSans.variable} ${geistMono.variable} antialiased transition-theme min-h-screen bg-background text-foreground`}
      >
        <ThemeProvider>
          <AuthProvider>
            <ThemeInitializer />
            <MantineThemeProvider>{children}</MantineThemeProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
