"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { exercisesApi } from "@/lib/api";

/**
 * Danh sách các category để lọc
 */
const categories = [
  "Tất cả",
  "Tìm kiếm",
  "Sắp xếp",
  "Cấu trúc dữ liệu",
  "Đồ thị",
  "Quy hoạch động",
  "Đệ quy",
];

/**
 * Danh sách các mức độ Advanced để lọc
 */
const difficulties = ["Tất cả", "Beginner", "Intermediate", "Advanced"];

/**
 * Component hiển thị màu tương ứng với độ Advanced
 *
 * @param {Object} props - Props của component
 * @param {string} props.difficulty - Độ Advanced của bài tập
 * @returns {JSX.Element} Badge hiển thị độ Advanced
 */
const DifficultyBadge = ({ difficulty }: { difficulty: string }) => {
  let colorClass = "";

  switch (difficulty) {
    case "Beginner":
      colorClass =
        "bg-green-100 light:text-foreground dark:bg-green-900/30 dark:text-green-300";
      break;
    case "Intermediate":
      colorClass =
        "light:bg-yellow-600 light:text-white dark:bg-yellow-900/30 dark:text-yellow-300";
      break;
    case "Advanced":
      colorClass =
        "light:bg-red-500 light:text-white dark:bg-red-900/30 dark:text-red-300";
      break;
    default:
      colorClass =
        "bg-gray-100 light:text-gray-800 dark:bg-gray-700 dark:text-gray-300";
  }

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${colorClass}`}>
      {difficulty}
    </span>
  );
};

/**
 * Trang danh sách bài tập
 *
 * @returns {JSX.Element} Trang hiển thị danh sách bài tập
 */
export default function ExercisesPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("Tất cả");
  const [difficultyFilter, setDifficultyFilter] = useState("Tất cả");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [items, setItems] = useState<
    Array<{
      id: number;
      title: string;
      description: string;
      category: string;
      difficulty: "Beginner" | "Intermediate" | "Advanced";
      estimatedTime: string;
      completionRate: number;
      completed: boolean;
    }>
  >([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const list = await exercisesApi.listExercises(1, 50);
        const mapped = list.map((ex: any) => {
          const diffMap: Record<
            string,
            "Beginner" | "Intermediate" | "Advanced"
          > = {
            easy: "Beginner",
            medium: "Intermediate",
            hard: "Advanced",
          };
          const d =
            diffMap[String(ex?.difficulty || "medium").toLowerCase()] ||
            "Intermediate";
          return {
            id: ex.id,
            title: ex?.title || ex?.name || "",
            description: ex?.description || "",
            category: ex?.category || "Thuật toán",
            difficulty: d,
            estimatedTime: ex?.estimatedTime || "",
            completionRate: ex?.completionRate || 0,
            completed: ex?.completed || false,
          };
        });
        setItems(mapped);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Lọc bài tập theo các điều kiện (trên dữ liệu thực)
  const filteredExercises = useMemo(() => {
    const base = items;
    return base.filter((exercise) => {
      const titleLc = String(exercise.title || "").toLowerCase();
      const descLc = String(exercise.description || "").toLowerCase();
      const searchLc = searchTerm.toLowerCase();
      const matchesSearch =
        titleLc.includes(searchLc) || descLc.includes(searchLc);
      const matchesCategory =
        categoryFilter === "Tất cả" || exercise.category === categoryFilter;
      const matchesDifficulty =
        difficultyFilter === "Tất cả" ||
        exercise.difficulty === difficultyFilter;
      return matchesSearch && matchesCategory && matchesDifficulty;
    });
  }, [items, searchTerm, categoryFilter, difficultyFilter]);

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header và tiêu đề */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Bài tập</h1>
        <p className="text-foreground/70">
          Thực hành và làm chủ giải thuật với các bài tập đa dạng theo mức độ
          Advanced tăng dần.
        </p>
      </div>

      {/* Bộ lọc và tìm kiếm */}
      <div className="mb-8 bg-background border border-foreground/10 rounded-lg p-4 shadow-sm theme-transition">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Tìm kiếm */}
          <div className="col-span-1 md:col-span-2">
            <label
              htmlFor="search"
              className="block text-sm font-medium text-foreground/70 mb-1">
              Tìm kiếm bài tập
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg
                  className="h-5 w-5 text-foreground/40"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <input
                type="text"
                id="search"
                className="block w-full pl-10 pr-3 py-2 border border-foreground/10 rounded-md bg-background text-foreground placeholder-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-transparent transition-colors theme-transition"
                placeholder="Tìm kiếm theo tên hoặc mô tả..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {/* Lọc theo danh mục */}
          <div>
            <label
              htmlFor="category"
              className="block text-sm font-medium text-foreground/70 mb-1">
              Danh mục
            </label>
            <select
              id="category"
              className="block w-full py-2 px-3 border border-foreground/10 rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-transparent transition-colors theme-transition"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Lọc theo Trình độ */}
          <div>
            <label
              htmlFor="difficulty"
              className="block text-sm font-medium text-foreground/70 mb-1">
              Trình độ
            </label>
            <select
              id="difficulty"
              className="block w-full py-2 px-3 border border-foreground/10 rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-transparent transition-colors theme-transition"
              value={difficultyFilter}
              onChange={(e) => setDifficultyFilter(e.target.value)}>
              {difficulties.map((difficulty) => (
                <option key={difficulty} value={difficulty}>
                  {difficulty}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Toggle chế độ xem */}
        <div className="mt-4 flex justify-end border-t border-foreground/5 pt-4">
          <div className="inline-flex rounded-md shadow-sm">
            <button
              type="button"
              aria-label="Chuyển sang dạng lưới"
              className={`px-4 py-2 text-sm font-medium rounded-l-md border focus:z-10 focus:outline-none transition-colors ${
                viewMode === "grid"
                  ? "bg-primary/10 border-primary/30 text-primary"
                  : "bg-background border-foreground/10 text-foreground/70 hover:bg-foreground/5"
              }`}
              onClick={() => setViewMode("grid")}>
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
                  d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                />
              </svg>
            </button>
            <button
              type="button"
              aria-label="Chuyển sang dạng danh sách"
              className={`px-4 py-2 text-sm font-medium rounded-r-md border focus:z-10 focus:outline-none transition-colors ${
                viewMode === "list"
                  ? "bg-primary/10 border-primary/30 text-primary"
                  : "bg-background border-foreground/10 text-foreground/70 hover:bg-foreground/5"
              }`}
              onClick={() => setViewMode("list")}>
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
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Hiển thị kết quả lọc */}
      <div className="mb-4">
        <p className="text-foreground/60">
          {loading
            ? "Đang tải..."
            : `Hiển thị ${filteredExercises.length} bài tập`}
          {categoryFilter !== "Tất cả" && ` trong danh mục "${categoryFilter}"`}
          {difficultyFilter !== "Tất cả" &&
            ` với độ Advanced "${difficultyFilter}"`}
          {searchTerm && ` khớp với từ Advanceda "${searchTerm}"`}
        </p>
      </div>

      {/* Danh sách bài tập - Chế độ lưới */}
      {viewMode === "grid" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredExercises.map((exercise) => (
            <div
              key={exercise.id}
              className="border border-foreground/10 rounded-lg overflow-hidden bg-background hover:shadow-md transition-all theme-transition">
              <div className="p-5">
                {/* Header với badge hoàn thành */}
                <div className="flex justify-between items-start mb-3">
                  <DifficultyBadge difficulty={exercise.difficulty} />
                  {exercise.completed && (
                    <span className="bg-primary/10 text-primary rounded-full px-2 py-0.5 text-xs font-medium">
                      Đã hoàn thành
                    </span>
                  )}
                </div>

                {/* Tiêu đề và mô tả */}
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {exercise.title}
                </h3>
                <p className="text-foreground/70 text-sm mb-4 line-clamp-2">
                  {exercise.description}
                </p>

                {/* Thông tin bổ sung */}
                <div className="flex flex-wrap gap-y-2 text-sm text-foreground/60 mb-4">
                  <div className="w-full sm:w-1/2 flex items-center">
                    <svg
                      className="h-4 w-4 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                      />
                    </svg>
                    {exercise.category}
                  </div>
                  <div className="w-full sm:w-1/2 flex items-center">
                    <svg
                      className="h-4 w-4 mr-1"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    {exercise.estimatedTime}
                  </div>
                </div>

                {/* Thanh tiến độ */}
                <div className="mb-4">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-foreground/60">Tỷ lệ hoàn thành</span>
                    <span className="font-medium text-foreground/80">
                      {exercise.completionRate}%
                    </span>
                  </div>
                  <div className="w-full bg-foreground/10 rounded-full h-1.5">
                    <div
                      className="bg-primary h-1.5 rounded-full"
                      style={{ width: `${exercise.completionRate}%` }}></div>
                  </div>
                </div>

                {/* Nút làm bài */}
                <Link
                  href={`/exercises/${exercise.id}`}
                  className="block w-full py-2 px-4 bg-primary text-white rounded-md text-center font-medium hover:bg-primary/90 transition-colors">
                  {exercise.completed ? "Làm lại" : "Bắt đầu làm"}
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Danh sách bài tập - Chế độ danh sách */}
      {viewMode === "list" && (
        <div className="border border-foreground/10 rounded-lg overflow-hidden theme-transition">
          <table className="min-w-full divide-y divide-foreground/10">
            <thead className="bg-foreground/5">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">
                  Bài tập
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">
                  Danh mục
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">
                  Trình độ
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">
                  Thời gian
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">
                  Tỷ lệ hoàn thành
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-foreground/70 uppercase tracking-wider">
                  Trạng thái
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-right text-xs font-medium text-foreground/70 uppercase tracking-wider">
                  Hành động
                </th>
              </tr>
            </thead>
            <tbody className="bg-background divide-y divide-foreground/10">
              {filteredExercises.map((exercise) => (
                <tr
                  key={exercise.id}
                  className="hover:bg-foreground/5 transition-colors">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-foreground">
                        {exercise.title}
                      </div>
                      <div className="text-sm text-foreground/60 line-clamp-1">
                        {exercise.description}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground/70">
                    {exercise.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <DifficultyBadge difficulty={exercise.difficulty} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground/70">
                    {exercise.estimatedTime}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-full bg-foreground/10 rounded-full h-1.5 mr-2">
                        <div
                          className="bg-primary h-1.5 rounded-full"
                          style={{
                            width: `${exercise.completionRate}%`,
                          }}></div>
                      </div>
                      <span className="text-xs text-foreground/70">
                        {exercise.completionRate}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {exercise.completed ? (
                      <span className="bg-primary/10 text-primary rounded-full px-2 py-0.5 text-xs font-medium">
                        Đã hoàn thành
                      </span>
                    ) : (
                      <span className="bg-foreground/10 text-foreground/60 rounded-full px-2 py-0.5 text-xs font-medium">
                        Chưa hoàn thành
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link
                      href={`/exercises/${exercise.id}`}
                      className="text-primary hover:text-primary/80 transition-colors">
                      {exercise.completed ? "Làm lại" : "Bắt đầu làm"}
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Không có kết quả */}
      {filteredExercises.length === 0 && (
        <div className="text-center py-12 bg-foreground/5 rounded-lg border border-foreground/10">
          <svg
            className="mx-auto h-12 w-12 text-foreground/30"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
              d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-foreground">
            Không tìm thấy bài tập
          </h3>
          <p className="mt-2 text-foreground/60">
            Không có bài tập nào khớp với điều kiện tìm kiếm. Hãy thử điều chỉnh
            bộ lọc.
          </p>
          <button
            onClick={() => {
              setSearchTerm("");
              setCategoryFilter("Tất cả");
              setDifficultyFilter("Tất cả");
            }}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary/50">
            Xóa bộ lọc
          </button>
        </div>
      )}
    </div>
  );
}
