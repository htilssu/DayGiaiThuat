"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { lessonsApi, Lesson } from "@/lib/api";

interface LessonPageProps {
  topicId: string;
  lessonId: string;
}

export default function LessonPage({ topicId, lessonId }: LessonPageProps) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLessonData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch lesson by external ID
        const lessonData = await lessonsApi.getLessonByExternalId(lessonId);
        setLesson(lessonData);
      } catch (err) {
        console.error("Lỗi khi tải dữ liệu bài học:", err);
        setError("Không thể tải thông tin bài học. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };

    if (lessonId) {
      fetchLessonData();
    }
  }, [lessonId]);

  if (isLoading) {
    return (
      <div className="min-h-screen pb-20">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-10">
            <div className="h-4 bg-foreground/10 rounded w-32 mb-4 animate-pulse"></div>
            <div className="h-8 bg-foreground/10 rounded w-64 mb-2 animate-pulse"></div>
            <div className="h-4 bg-foreground/10 rounded w-96 animate-pulse"></div>
          </div>
          <div className="max-w-4xl mx-auto">
            <div className="space-y-6">
              {[...Array(3)].map((_, i) => (
                <div
                  key={i}
                  className="bg-white rounded-xl p-6 shadow-sm border border-foreground/10">
                  <div className="h-6 bg-foreground/10 rounded w-48 mb-4 animate-pulse"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-foreground/10 rounded w-full animate-pulse"></div>
                    <div className="h-4 bg-foreground/10 rounded w-3/4 animate-pulse"></div>
                    <div className="h-4 bg-foreground/10 rounded w-1/2 animate-pulse"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="min-h-screen pb-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-20">
            <h1 className="text-2xl font-bold mb-4">Không tìm thấy bài học</h1>
            <p className="text-foreground/70 mb-6">
              {error || "Bài học không tồn tại hoặc đã bị xóa"}
            </p>
            <Link
              href={`/topics/${topicId}`}
              className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
              ← Quay lại chủ đề
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const renderSection = (section: any, index: number) => {
    switch (section.type) {
      case "text":
        return (
          <div
            key={index}
            className="bg-white rounded-xl p-6 shadow-sm border border-foreground/10">
            <div className="prose max-w-none">
              <div dangerouslySetInnerHTML={{ __html: section.content }} />
            </div>
          </div>
        );
      case "code":
        return (
          <div
            key={index}
            className="bg-white rounded-xl p-6 shadow-sm border border-foreground/10">
            <h3 className="text-lg font-semibold mb-3">Code Example</h3>
            <pre className="bg-foreground/5 rounded-lg p-4 overflow-x-auto">
              <code>{section.content}</code>
            </pre>
          </div>
        );
      case "quiz":
        return (
          <div
            key={index}
            className="bg-white rounded-xl p-6 shadow-sm border border-foreground/10">
            <h3 className="text-lg font-semibold mb-3">Câu hỏi</h3>
            <div className="prose max-w-none mb-4">
              <div dangerouslySetInnerHTML={{ __html: section.content }} />
            </div>
            {section.options && (
              <div className="space-y-2">
                {Object.entries(section.options).map(
                  ([key, value]: [string, any]) => (
                    <label
                      key={key}
                      className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="radio"
                        name={`quiz-${index}`}
                        value={key}
                        className="text-primary"
                      />
                      <span>{value}</span>
                    </label>
                  )
                )}
              </div>
            )}
            {section.answer !== undefined && (
              <div className="mt-4 p-3 bg-foreground/5 rounded-lg">
                <strong>Đáp án:</strong> {section.answer}
                {section.explanation && (
                  <div className="mt-2 text-sm text-foreground/70">
                    {section.explanation}
                  </div>
                )}
              </div>
            )}
          </div>
        );
      default:
        return (
          <div
            key={index}
            className="bg-white rounded-xl p-6 shadow-sm border border-foreground/10">
            <div className="prose max-w-none">
              <div dangerouslySetInnerHTML={{ __html: section.content }} />
            </div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen pb-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-10">
          <Link
            href={`/topics/${topicId}`}
            className="text-primary hover:underline mb-2 inline-block">
            ← Quay lại chủ đề
          </Link>
          <div className="mb-4">
            <h1 className="text-3xl md:text-4xl font-bold mb-2">
              {lesson.title}
            </h1>
            <p className="text-foreground/70 text-lg">{lesson.description}</p>
          </div>
        </div>

        {/* Navigation */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            {lesson.prev_lesson_id && (
              <Link
                href={`/topics/${topicId}/lessons/${lesson.prev_lesson_id}`}
                className="inline-flex items-center px-4 py-2 bg-foreground/5 rounded-lg hover:bg-foreground/10 transition">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                Bài trước
              </Link>
            )}
          </div>
          <div>
            {lesson.next_lesson_id && (
              <Link
                href={`/topics/${topicId}/lessons/${lesson.next_lesson_id}`}
                className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition">
                Bài tiếp theo
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 ml-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </Link>
            )}
          </div>
        </div>

        {/* Lesson Content */}
        <div className="max-w-4xl mx-auto">
          <div className="space-y-6">
            {lesson.sections.map((section, index) =>
              renderSection(section, index)
            )}
          </div>
        </div>

        {/* Exercise */}
        {lesson.exercise && (
          <div className="max-w-4xl mx-auto mt-12">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-foreground/10">
              <h2 className="text-2xl font-bold mb-4">Bài tập</h2>
              <div className="mb-4">
                <h3 className="text-xl font-semibold mb-2">
                  {lesson.exercise.name}
                </h3>
                <p className="text-foreground/70 mb-4">
                  {lesson.exercise.description}
                </p>
                {lesson.exercise.constraint && (
                  <div className="mb-4 p-3 bg-foreground/5 rounded-lg">
                    <strong>Ràng buộc:</strong> {lesson.exercise.constraint}
                  </div>
                )}
                {lesson.exercise.suggest && (
                  <div className="mb-4 p-3 bg-primary/10 rounded-lg">
                    <strong>Gợi ý:</strong> {lesson.exercise.suggest}
                  </div>
                )}
              </div>
              <Link
                href={`/exercises/${lesson.exercise.id}`}
                className="inline-flex items-center px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
                Làm bài tập
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 ml-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
