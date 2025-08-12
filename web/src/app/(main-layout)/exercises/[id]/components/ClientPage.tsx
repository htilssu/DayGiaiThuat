"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ExerciseDetail } from "./types";
import { exercisesApi } from "@/lib/api";
import ExerciseSubmission from "./ExerciseSubmission";
import ExerciseHeader from "./ExerciseHeader";
import ExerciseContent from "./ExerciseContent";

/**
 * Component client-side cho trang chi tiết bài tập
 *
 * @param {Object} props - Props của component
 * @param {ExerciseDetail} props.exercise - Thông tin chi tiết bài tập
 * @returns {JSX.Element} Component client-side cho trang chi tiết bài tập
 */
export default function ClientPage({ exercise }: { exercise: ExerciseDetail }) {
  const router = useRouter();
  const [userCode, setUserCode] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState<"description" | "submission">(
    "description"
  );

  // Khởi tạo dữ liệu ban đầu
  useEffect(() => {
    setUserCode(exercise.codeTemplate || "");
    setIsLoading(false);
  }, [exercise]);

  const handleSubmit = async () => {
    try {
      // Gửi cập nhật trạng thái hoàn thành lên server
      await exercisesApi.updateExercise(exercise.id, { completed: true });
      alert("Bài tập đã được nộp thành công!");
      // Làm mới dữ liệu để phản ánh trạng thái mới từ server
      router.refresh();
    } catch (e) {
      // Thông báo đơn giản khi thất bại
      alert("Cập nhật trạng thái hoàn thành thất bại. Vui lòng thử lại.");
    }
  };

  // Hiển thị trạng thái đang tải
  if (isLoading) {
    return (
      <div className="container mx-auto p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
          <span className="ml-3 text-foreground/60">Đang tải bài tập...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 md:p-8 max-w-6xl">
      {/* Breadcrumb */}
      <div className="mb-6 text-sm text-foreground/60">
        <Link href="/exercises" className="hover:text-primary">
          Danh sách bài tập
        </Link>{" "}
        / <span className="text-foreground/90">{exercise.title}</span>
      </div>

      {/* Exercise Header */}
      <ExerciseHeader exercise={exercise} />

      {/* Tabs */}
      <div className="flex border-b border-foreground/10 mt-8 mb-6">
        <button
          className={`px-4 py-2 font-medium text-sm ${
            currentTab === "description"
              ? "text-primary border-b-2 border-primary"
              : "text-foreground/60 hover:text-foreground/90"
          }`}
          onClick={() => setCurrentTab("description")}>
          Mô tả bài tập
        </button>
        <button
          className={`px-4 py-2 font-medium text-sm ${
            currentTab === "submission"
              ? "text-primary border-b-2 border-primary"
              : "text-foreground/60 hover:text-foreground/90"
          }`}
          onClick={() => setCurrentTab("submission")}>
          Làm bài
        </button>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {currentTab === "description" ? (
          <ExerciseContent content={exercise.content} />
        ) : (
          <ExerciseSubmission exercise={exercise} onSubmit={handleSubmit} />
        )}
      </div>
    </div>
  );
}
