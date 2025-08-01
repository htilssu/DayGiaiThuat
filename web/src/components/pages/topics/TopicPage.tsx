"use client";

import { Lesson, topicsApi, TopicWithLessons } from "@/lib/api";
import Link from "next/link";
import { useEffect, useState } from "react";

interface TopicPageProps {
  topicId: string;
}

export default function TopicPage({ topicId }: TopicPageProps) {
  const [topic, setTopic] = useState<TopicWithLessons | null>(null);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTopicData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch topic with lessons
        const topicData = await topicsApi.getTopicWithLessons(
          parseInt(topicId)
        );
        setTopic(topicData);
        setLessons(topicData.lessons);
      } catch (err) {
        console.error("Lỗi khi tải dữ liệu chủ đề:", err);
        setError("Không thể tải thông tin chủ đề. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };

    if (topicId) {
      fetchTopicData();
    }
  }, [topicId]);

  if (isLoading) {
    return (
      <div className="min-h-screen pb-20">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-10">
            <div className="h-4 bg-foreground/10 rounded w-32 mb-4 animate-pulse"></div>
            <div className="flex items-center gap-4 mb-4">
              <div className="w-16 h-16 rounded-full bg-foreground/10 animate-pulse"></div>
              <div className="flex-1">
                <div className="h-8 bg-foreground/10 rounded w-64 mb-2 animate-pulse"></div>
                <div className="h-4 bg-foreground/10 rounded w-96 animate-pulse"></div>
              </div>
            </div>
          </div>
          <div className="max-w-3xl mx-auto">
            <div className="h-8 bg-foreground/10 rounded w-48 mb-6 animate-pulse"></div>
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="bg-white rounded-xl p-6 shadow-sm border border-foreground/10">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-foreground/10 animate-pulse"></div>
                    <div className="flex-1">
                      <div className="h-6 bg-foreground/10 rounded w-48 mb-2 animate-pulse"></div>
                      <div className="h-4 bg-foreground/10 rounded w-64 animate-pulse"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="min-h-screen pb-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-20">
            <h1 className="text-2xl font-bold mb-4">Không tìm thấy chủ đề</h1>
            <p className="text-foreground/70 mb-6">
              {error || "Chủ đề không tồn tại hoặc đã bị xóa"}
            </p>
            <Link
              href="/learn"
              className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
              ← Quay lại lộ trình
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <details
      key={topic.id}
      className="group bg-foreground/5 rounded-xl overflow-hidden"
      open={topic.id === 1}>
      <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-foreground/10">
        <div>
          <h3 className="font-medium">{topic.name}</h3>
          <p className="text-sm text-foreground/70 mt-1">{topic.description}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-foreground/70">
            {/* {topic.lessons.length} bài học */}0 bài học
          </div>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5 transform transition-transform group-open:rotate-180"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </summary>
      <div className="border-t border-foreground/10">
        {/* {topic.lessons.map((lesson) => (
                        <div
                          key={lesson.id}
                          className="flex items-center gap-4 p-4 hover:bg-foreground/5">
                          <div
                            className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center bg-green-500/10 text-green-500`}>
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              className="h-5 w-5"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor">
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                              />
                            </svg>
                          </div>
                          <div className="flex-grow">
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium">{lesson.title}</h4>
                            </div>
                            <p className="text-sm text-foreground/70 mt-1">
                              {lesson.description}
                            </p>
                          </div>
                          <div className="flex items-center gap-3 flex-shrink-0">
                            <span className="text-sm text-foreground/70">
                              {lesson.sections &&
                              lesson.sections.length > 0 &&
                              lesson.sections[0].order
                                ? `${lesson.sections[0].order} phút`
                                : ""}
                            </span>
                            <Link
                              href={`/topics/${topic.id}/lessons/${lesson.external_id}`}
                              className="px-3 py-1 text-sm border border-primary text-primary rounded hover:bg-primary/10 transition">
                              Xem ngay
                            </Link>
                          </div>
                        </div>
                      ))} */}
      </div>
    </details>
  );
}
