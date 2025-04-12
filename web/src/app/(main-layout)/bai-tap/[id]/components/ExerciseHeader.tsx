"use client";

import Link from "next/link";
import { ExerciseDetail } from "./types";

/**
 * Component hiển thị độ khó của bài tập bằng màu
 *
 * @param {Object} props - Props của component
 * @param {string} props.difficulty - Độ khó của bài tập
 * @returns {JSX.Element} Badge hiển thị độ khó
 */
const DifficultyBadge = ({ difficulty }: { difficulty: string }) => {
  let colorClass = "";

  if (difficulty === "Dễ") {
    colorClass =
      "bg-green-200 text-green-900 dark:bg-green-900/30 dark:text-green-300";
  } else if (difficulty === "Trung bình") {
    colorClass =
      "bg-yellow-200 text-yellow-900 dark:bg-yellow-900/30 dark:text-yellow-300";
  } else if (difficulty === "Khó") {
    colorClass = "bg-red-200 text-red-900 dark:bg-red-900/30 dark:text-red-300";
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass} theme-transition`}
    >
      {difficulty}
    </span>
  );
};

/**
 * Component hiển thị phần header của bài tập
 *
 * @param {Object} props - Props của component
 * @param {ExerciseDetail} props.exercise - Thông tin chi tiết bài tập
 * @returns {JSX.Element} Header bài tập
 */
export default function ExerciseHeader({
  exercise,
}: {
  exercise: ExerciseDetail;
}) {
  return (
    <div className="mb-8">
      {/* Breadcrumb */}
      <div className="flex items-center text-sm mb-4 text-foreground/60">
        <Link href="/bai-tap" className="hover:text-primary transition-colors">
          Bài tập
        </Link>
        <svg
          className="mx-2 h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            d="M9 5l7 7-7 7"
          />
        </svg>
        <span className="truncate">{exercise.title}</span>
      </div>

      {/* Tiêu đề và thông tin */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-2">
            {exercise.title}
          </h1>
          <p className="text-foreground/70 mb-4">{exercise.description}</p>

          {/* Thông tin bổ sung */}
          <div className="flex flex-wrap gap-3 mb-2">
            <div className="flex items-center">
              <DifficultyBadge difficulty={exercise.difficulty} />
            </div>
            <div className="flex items-center text-foreground/60 text-sm">
              <svg
                className="h-4 w-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                />
              </svg>
              {exercise.category}
            </div>
            <div className="flex items-center text-foreground/60 text-sm">
              <svg
                className="h-4 w-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {exercise.estimatedTime}
            </div>
            <div className="flex items-center text-foreground/60 text-sm">
              <svg
                className="h-4 w-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              {exercise.completionRate}% hoàn thành
            </div>
            {exercise.completed && (
              <div className="flex items-center text-primary text-sm">
                <svg
                  className="h-4 w-4 mr-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Đã hoàn thành
              </div>
            )}
          </div>
        </div>

        {/* Nút bắt đầu làm */}
        <div className="mt-4 md:mt-0 md:ml-4">
          <Link
            href={`/bai-tap/${exercise.id}?tab=submission`}
            className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
          >
            {exercise.completed ? "Làm lại" : "Bắt đầu làm"}
          </Link>
        </div>
      </div>

      {/* Thanh phân cách */}
      <div className="mt-6 border-b border-foreground/10"></div>
    </div>
  );
}
