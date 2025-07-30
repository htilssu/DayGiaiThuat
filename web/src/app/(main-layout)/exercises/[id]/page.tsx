import { Suspense } from "react";
import { exercisesData } from "@/data/mockExercises";
import ClientPage from "./components/ClientPage";

/**
 * Trang chi tiết bài tập (Server Component)
 *
 * @param {Object} props - Props của component
 * @param {Object} props.params - Tham số của trang
 * @param {string|number} props.params.id - ID của bài tập
 * @returns {JSX.Element} Trang chi tiết bài tập
 */
export default async function ExerciseDetailPage({
  params,
}: {
  params: Promise<{ id: string | number }>;
}) {
  // Lấy dữ liệu bài tập từ ID
  const pr = await params;
  const exerciseId = typeof pr.id === "string" ? Number(pr.id) : pr.id;
  const exerciseRaw = exercisesData.find((ex) => ex.id === exerciseId);
  if (!exerciseRaw) {
    return (
      <div className="container mx-auto p-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg dark:bg-red-900/20 dark:border-red-900/30 dark:text-red-400">
          <p className="font-medium">Không tìm thấy bài tập</p>
          <p className="mt-1">Bài tập với ID {exerciseId} không tồn tại.</p>
        </div>
      </div>
    );
  }

  // Map difficulty to Vietnamese
  const difficultyMap: Record<string, string> = {
    Beginner: "Dễ",
    Intermediate: "Trung bình",
    Advanced: "Khó",
  };
  const exercise = {
    ...exerciseRaw,
    difficulty: (difficultyMap[exerciseRaw.difficulty] ||
      exerciseRaw.difficulty) as "Dễ" | "Trung bình" | "Khó",
  };

  return (
    <Suspense fallback={<div>Đang tải...</div>}>
      <ClientPage exercise={exercise} />
    </Suspense>
  );
}
