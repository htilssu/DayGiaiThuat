"use client";

import { AdminHeader } from "@/components/admin/Header";
import Footer from "@/components/ui/Footer";
import { Geist, Geist_Mono } from "next/font/google";
import { useEffect } from "react";
import "../globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function AdminLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Apply admin theme colors
  useEffect(() => {
    // Update CSS variables for admin theme
    document.documentElement.style.setProperty("--color-primary", "98 182 159"); // Seafoam green
    document.documentElement.style.setProperty(
      "--color-secondary",
      "173 216 230"
    ); // Light blue
    document.documentElement.style.setProperty("--color-accent", "135 206 235"); // Sky blue

    // Cleanup when component unmounts
    return () => {
      // Reset to default theme colors
      document.documentElement.style.removeProperty("--color-primary");
      document.documentElement.style.removeProperty("--color-secondary");
      document.documentElement.style.removeProperty("--color-accent");
    };
  }, []);

  return (
    <div
      className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen flex flex-col bg-background text-foreground transition-theme`}>
      <AdminHeader />
      <main className="flex-grow container mx-auto px-4 sm:px-6 py-8 md:py-12">
        {children}
      </main>
      <Footer />
    </div>
  );
}
