"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { useTheme } from "@/contexts/ThemeContext";

/**
 * Component hiển thị nội dung bài tập dạng Markdown
 *
 * @param {Object} props - Props của component
 * @param {string} props.content - Nội dung Markdown
 * @returns {JSX.Element} Nội dung bài tập đã được render
 */
export default function ExerciseContent({ content }: { content: string }) {
  const { theme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Đảm bảo rằng component chỉ được render ở client-side
  useEffect(() => {
    setMounted(true);
  }, []);

  // Tạm hiển thị skeleton trong khi đợi hydration
  if (!mounted) {
    return (
      <div className="prose prose-lg mx-auto theme-transition animate-pulse">
        <div className="h-8 bg-foreground/10 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-foreground/10 rounded w-full mb-2"></div>
        <div className="h-4 bg-foreground/10 rounded w-5/6 mb-2"></div>
        <div className="h-4 bg-foreground/10 rounded w-4/6 mb-6"></div>

        <div className="h-6 bg-foreground/10 rounded w-1/4 mb-3"></div>
        <div className="h-4 bg-foreground/10 rounded w-full mb-2"></div>
        <div className="h-4 bg-foreground/10 rounded w-5/6 mb-4"></div>

        <div className="h-32 bg-foreground/10 rounded w-full mb-6"></div>

        <div className="h-6 bg-foreground/10 rounded w-1/4 mb-3"></div>
        <div className="h-4 bg-foreground/10 rounded w-full mb-2"></div>
        <div className="h-4 bg-foreground/10 rounded w-full mb-2"></div>
      </div>
    );
  }

  return (
    <div className="prose prose-lg mx-auto dark:prose-invert prose-headings:text-foreground prose-p:text-foreground/80 prose-a:text-primary theme-transition prose-code:text-foreground/90">
      <ReactMarkdown
        components={{
          // Tùy chỉnh cách hiển thị code
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || "");
            return match ? (
              <SyntaxHighlighter
                style={oneDark as any}
                language={match[1]}
                PreTag="div"
                className="rounded-md border border-foreground/10 bg-foreground/5 theme-transition"
              >
                {String(children).replace(/\n$/, "")}
              </SyntaxHighlighter>
            ) : (
              <code
                className="bg-foreground/10 rounded px-1 py-0.5 text-foreground/90 theme-transition"
                {...props}
              >
                {children}
              </code>
            );
          },
          // Tùy chỉnh hiển thị tiêu đề
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold border-b border-foreground/10 pb-2 mb-4 theme-transition">
              {children}
            </h1>
          ),
          // Tùy chỉnh danh sách
          ul: ({ children }) => (
            <ul className="list-disc pl-5 space-y-2 my-4 text-foreground/80 theme-transition">
              {children}
            </ul>
          ),
          // Tùy chỉnh liên kết
          a: ({ href, children }) => (
            <a
              href={href}
              className="text-primary hover:text-primary/80 transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
