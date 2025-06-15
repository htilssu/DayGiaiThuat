"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { coursesApi, Course } from "@/lib/api";

/**
 * Component hiển thị danh sách khóa học
 */
export default function CourseListPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [currentPage, setCurrentPage] = useState<number>(1);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setIsLoading(true);
        const response = await coursesApi.getCourses(currentPage, 6);
        setCourses(response.items);
        setTotalPages(response.totalPages);
        setError(null);
      } catch (err) {
        console.error("Lỗi khi tải khóa học:", err);
        setError("Không thể tải danh sách khóa học. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCourses();
  }, [currentPage]);

  // Xử lý chuyển trang
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Chuyển đổi phút thành định dạng giờ:phút
  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours > 0 ? `${hours} giờ ` : ""}${mins > 0 ? `${mins} phút` : ""
      }`;
  };

  return (
    <div className="py-10 px-4 max-w-7xl mx-auto">
      {/* Banner */}
      <div className="relative w-full h-80 mb-12 overflow-hidden rounded-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary opacity-90 z-10"></div>
        <div className="absolute inset-0 bg-grid-white z-0"></div>
        <div className="absolute inset-0 flex flex-col justify-center items-center text-white z-20 p-6 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 animate-fade-in">
            Khóa Học Thuật Toán
          </h1>
          <p
            className="text-lg md:text-xl max-w-3xl animate-fade-in"
            style={{ animationDelay: "0.2s" }}
          >
            Nâng cao kỹ năng lập trình và tư duy giải quyết vấn đề với các khóa
            học chất lượng cao
          </p>
        </div>
      </div>

      {/* Filter & Search - có thể phát triển thêm */}
      <div className="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <h2 className="text-3xl font-bold">Tất Cả Khóa Học</h2>
        <div className="relative w-full md:w-64">
          <input
            type="text"
            placeholder="Tìm kiếm khóa học..."
            className="w-full py-2 px-4 rounded-lg border border-foreground/20 bg-background"
          />
        </div>
      </div>

      {/* Danh sách khóa học */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="bg-foreground/5 rounded-xl p-4 h-96 animate-pulse"
            ></div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-10">
          <p className="text-lg text-accent">{error}</p>
          <button
            onClick={() => setCurrentPage(1)}
            className="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition"
          >
            Thử lại
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {courses.map((course) => (
              <Link href={`/courses/${course.id}`} key={course.id}>
                <div className="group bg-background rounded-xl overflow-hidden border border-foreground/10 hover:border-primary transition-all duration-300 h-full flex flex-col">
                  {/* Thumbnail */}
                  <div className="relative w-full h-48 overflow-hidden">
                    {course.thumbnailUrl ? (
                      <Image
                        src={course.thumbnailUrl}
                        alt={course.title}
                        fill
                        className="object-cover transform group-hover:scale-105 transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
                        <span className="text-4xl text-primary">Α</span>
                      </div>
                    )}
                    <div className="absolute top-2 right-2 bg-background/80 backdrop-blur-sm text-foreground text-sm font-medium py-1 px-3 rounded-full">
                      {course.level}
                    </div>
                    {course.price > 0 ? (
                      <div className="absolute bottom-2 left-2 bg-accent/90 text-white text-sm font-medium py-1 px-3 rounded-full">
                        {course.price.toLocaleString("vi-VN")} ₫
                      </div>
                    ) : (
                      <div className="absolute bottom-2 left-2 bg-primary/90 text-white text-sm font-medium py-1 px-3 rounded-full">
                        Miễn phí
                      </div>
                    )}
                  </div>

                  {/* Nội dung */}
                  <div className="p-5 flex flex-col flex-grow">
                    <h3 className="font-bold text-xl mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                      {course.title}
                    </h3>
                    <p className="text-foreground/70 text-sm line-clamp-3 mb-4 flex-grow">
                      {course.description || "Không có mô tả cho khóa học này."}
                    </p>
                    <div className="mt-auto pt-3 border-t border-foreground/10 flex items-center justify-between">
                      <div className="flex items-center text-foreground/70 text-sm">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-4 w-4 mr-1"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        {formatDuration(course.duration)}
                      </div>
                      <div className="flex items-center text-primary font-medium">
                        Xem chi tiết
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* Phân trang */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-12">
              <div className="flex space-x-2">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 rounded-md border border-foreground/20 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-foreground/5"
                >
                  Trước
                </button>
                {[...Array(totalPages)].map((_, i) => (
                  <button
                    key={i}
                    onClick={() => handlePageChange(i + 1)}
                    className={`px-4 py-2 rounded-md border ${currentPage === i + 1
                        ? "bg-primary text-white border-primary"
                        : "border-foreground/20 hover:bg-foreground/5"
                      }`}
                  >
                    {i + 1}
                  </button>
                ))}
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 rounded-md border border-foreground/20 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-foreground/5"
                >
                  Sau
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
