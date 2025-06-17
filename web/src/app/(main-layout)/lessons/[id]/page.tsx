"use client";

import { useParams, useRouter } from "next/navigation";
import { dsaCourseContent, Lesson } from "@/data/courseContent";
import { useMemo } from "react";
import Link from "next/link";

export default function LessonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const lessonId = Number(params.id);

  // Find lesson and chapter
  const { lesson, chapter } = useMemo(() => {
    for (const chap of dsaCourseContent) {
      const found = chap.lessons.find((l) => l.id === lessonId);
      if (found) return { lesson: found, chapter: chap };
    }
    return { lesson: null, chapter: null };
  }, [lessonId]);

  if (!lesson) {
    return (
      <div className="py-16 px-4 max-w-2xl mx-auto text-center">
        <h1 className="text-2xl font-bold mb-4 text-accent">
          Bài học không tồn tại
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
        <button
          onClick={() => router.back()}
          className="text-primary hover:underline text-sm mb-2">
          ← Quay lại khóa học
        </button>
        <h2 className="text-lg text-foreground/70 font-medium mb-1">
          {chapter ? `Chương ${chapter.id}: ${chapter.title}` : ""}
        </h2>
        <h1 className="text-3xl font-bold mb-2">{lesson.title}</h1>
        <div className="flex items-center gap-4 text-sm text-foreground/60 mb-4">
          <span>
            {lesson.type === "video"
              ? "Video"
              : lesson.type === "quiz"
              ? "Quiz"
              : "Bài tập"}
          </span>
          <span>•</span>
          <span>{lesson.duration} phút</span>
        </div>
      </div>
      <div className="prose max-w-none mb-8">
        <p>{lesson.description}</p>
      </div>
      {/* Video or content placeholder */}
      {lesson.type === "video" && (
        <div className="w-full aspect-video bg-foreground/10 rounded-xl flex items-center justify-center text-2xl text-foreground/40">
          {lesson.videoUrl ? (
            <video
              controls
              src={lesson.videoUrl}
              className="w-full h-full rounded-xl"
            />
          ) : (
            "Video bài học sẽ hiển thị ở đây"
          )}
        </div>
      )}
      {lesson.type === "quiz" && (
        <div className="p-6 bg-purple-50 rounded-xl text-center text-purple-700">
          Quiz sẽ được phát triển sau.
        </div>
      )}
      {lesson.type === "exercise" && (
        <div className="mt-8 flex flex-col items-center gap-2">
          <Link
            href={`/exercises/${lesson.id}`}
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
