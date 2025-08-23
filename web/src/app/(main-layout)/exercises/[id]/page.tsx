import { Suspense } from "react";
import ClientPage from "./components/ClientPage";
import { exercisesApi } from "@/lib/api";

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
  let exercise;
  try {
    exercise = await exercisesApi.getExerciseDetailForUi(exerciseId);
  } catch (e) {
    return (
      <div className="container mx-auto p-8">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg dark:bg-red-900/20 dark:border-red-900/30 dark:text-red-400">
          <p className="font-medium">Không tải được bài tập</p>
          <p className="mt-1">Vui lòng thử lại sau.</p>
        </div>
      </div>
    );
  }

  return (
    <Suspense fallback={<div>Đang tải...</div>}>
      <ClientPage exercise={exercise} />
    </Suspense>
  );
}
