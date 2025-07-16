"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { lessonsApi, Lesson } from "@/lib/api";
import Link from "next/link";

export default function LessonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const lessonId = Number(params.id);

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLesson = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await lessonsApi.getLessonById(lessonId);
        setLesson(data);
      } catch {
        setError("Không thể tải thông tin bài học. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };
    if (lessonId) fetchLesson();
  }, [lessonId]);

  if (isLoading) {
    return (
      <div className="py-16 px-4 max-w-2xl mx-auto text-center">
        <div className="h-8 w-1/2 mx-auto bg-foreground/10 rounded mb-4 animate-pulse"></div>
        <div className="h-6 w-1/3 mx-auto bg-foreground/10 rounded mb-2 animate-pulse"></div>
        <div className="h-4 w-1/4 mx-auto bg-foreground/10 rounded mb-6 animate-pulse"></div>
        <div className="h-40 w-full bg-foreground/10 rounded mb-6 animate-pulse"></div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="py-16 px-4 max-w-2xl mx-auto text-center">
        <h1 className="text-2xl font-bold mb-4 text-accent">
          {error || "Bài học không tồn tại"}
        </h1>
        <p className="mb-6 text-foreground/70">
          Không tìm thấy bài học hoặc bài học đã bị xóa.
        </p>
        <button
          onClick={() => router.back()}
          className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
          Quay lại
        </button>
      </div>
    );
  }


  return (
    <div className="py-10 px-4 max-w-3xl mx-auto">
      <div className="mb-6">
        <Link
          href={lesson.topicId ? `/topics/${lesson.topicId}` : "/courses"}
          className="text-primary hover:underline text-sm mb-2">
          ← Quay lại {lesson.topicId ? "chủ đề" : "khóa học"}
        </Link>
        <h2 className="text-lg text-foreground/70 font-medium mb-1">
          {lesson.order ? `Bài ${lesson.order}` : ""}
        </h2>
        <h1 className="text-3xl font-bold mb-2">{lesson.title}</h1>
        <div className="flex items-center gap-4 text-sm text-foreground/60 mb-4">
          <span>Bài học</span>
          <span>•</span>
          <span>
            {lesson.sections &&
            lesson.sections.length > 0 &&
            lesson.sections[0].order
              ? `${lesson.sections[0].order} phút`
              : ""}
          </span>
        </div>
      </div>
      <div className="prose max-w-none mb-8">
        <p>{lesson.description}</p>
      </div>
      {/* Render lesson sections */}
      {lesson.sections &&
        lesson.sections.length > 0 &&
        lesson.sections.map((section, idx) => (
          <div key={idx} className="mb-8">
            {section.type === "text" && (
              <div
                className="prose max-w-none"
                dangerouslySetInnerHTML={{ __html: section.content }}
              />
            )}
            {section.type === "code" && (
              <pre className="bg-foreground/5 rounded-lg p-4 overflow-x-auto">
                <code>{section.content}</code>
              </pre>
            )}
            {section.type === "quiz" && (
              <div className="p-6 bg-purple-50 rounded-xl text-center text-purple-700">
                Quiz sẽ được phát triển sau.
              </div>
            )}
          </div>
        ))}
      {/* Exercise */}
      {lesson.exercise && (
        <div className="mt-8 flex flex-col items-center gap-2">
          <Link
            href={`/exercises/${lesson.exercise.id}`}
            className="inline-flex items-center gap-2 px-5 py-2 border-2 border-primary text-primary font-medium rounded-lg bg-white hover:bg-primary/10 transition-colors duration-150 shadow-sm">
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              strokeWidth={2}
              viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 20h9" />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M16.5 3.5a2.121 2.121 0 113 3L7 19.5 3 21l1.5-4L16.5 3.5z"
              />
            </svg>
            Làm bài tập
          </Link>
        </div>
      )}
    </div>
  );
}
