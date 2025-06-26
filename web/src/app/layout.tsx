import type { Metadata, Viewport } from "next";
import "./globals.css";
import ThemeInitializer from "../components/ThemeInitializer";
import HeadScripts from "./head-scripts";
import { MantineThemeProvider } from "@/components/MantineThemeProvider";
import ChatBot from "@/components/ChatBot/ChatBot";
import StoreWrapper from "@/components/wrapper/StoreWrapper";
import ModalWrapper from "@/components/wrapper/ModalWrapper";
import ClientWrapper from "@/components/wrapper/ClientWrapper";


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
        className={`antialiased transition-theme min-h-screen bg-background text-foreground`}>
        <StoreWrapper>
          <ClientWrapper>
            <ThemeInitializer />
            <MantineThemeProvider>
              <ModalWrapper>
                {children}
              </ModalWrapper>
              <ChatBot />
            </MantineThemeProvider>
          </ClientWrapper>
        </StoreWrapper>
      </body>
    </html>
  );
}
