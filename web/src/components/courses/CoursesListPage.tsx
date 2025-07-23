'use client';

import { CourseListItem, coursesApi } from "@/lib/api/courses";
import { useAppSelector } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Key, useState } from "react";
import Image from "next/image";

export default function CoursesListPage() {
    const [error, setError] = useState<string | null>(null);
    const [totalPages, setTotalPages] = useState<number>(1);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const router = useRouter();
    const userState = useAppSelector((state) => state.user);
    const { data: courses, isLoading } = useQuery({
        queryKey: ['courses', currentPage],
        queryFn: async () => {
            const data = await coursesApi.getCourses(currentPage, 6)
            setTotalPages(data.totalPages)
            return data.items as CourseListItem[];
        },
        enabled: !!userState.user,
    });

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

    // Xử lý khi click vào course card - navigate tới trang chi tiết
    const handleCourseClick = (courseId: number) => {
        router.push(`/courses/${courseId}`);
    };

    return (
        <div className="py-10 px-4 max-w-7xl mx-auto">
            {/* Banner */}
            <div className="relative w-full h-80 mb-12 overflow-hidden rounded-2xl">
                <div className="absolute inset-0 bg-primary/90 z-10"></div>
                <div className="absolute inset-0 bg-grid-white z-0"></div>
                <div className="absolute inset-0 flex flex-col justify-center items-center text-white z-20 p-6 text-center">
                    <h1 className="text-4xl md:text-5xl font-bold mb-4 animate-fade-in">
                        Khóa Học Thuật Toán
                    </h1>
                    <p
                        className="text-lg md:text-xl max-w-3xl animate-fade-in"
                        style={{ animationDelay: "0.2s" }}>
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
                    {[...Array(6)].map((_: any, i: Key | null | undefined) => (
                        <div
                            key={i}
                            className="bg-foreground/5 rounded-xl p-4 h-96 animate-pulse"></div>
                    ))}
                </div>
            ) : error ? (
                <div className="text-center py-10">
                    <p className="text-lg text-accent">{error}</p>
                    <button
                        onClick={() => setCurrentPage(1)}
                        className="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition">
                        Thử lại
                    </button>
                </div>
            ) : (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {courses!.map((course) => (
                            <div
                                key={course.id}
                                className="group bg-background rounded-xl overflow-hidden border border-foreground/10 hover:border-primary transition-all duration-300 h-full flex flex-col cursor-pointer"
                                onClick={() => handleCourseClick(course.id)}
                            >
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
                                    {/* Badge trạng thái đăng ký */}
                                    {course.isEnrolled && (
                                        <div className="absolute top-2 left-2 bg-primary text-white text-xs font-medium py-1 px-2 rounded-full">
                                            Đã đăng ký
                                        </div>
                                    )}
                                </div>

                                {/* Content */}
                                <div className="p-6 flex-1 flex flex-col">
                                    <h3 className="text-xl font-bold mb-2 group-hover:text-primary transition-colors line-clamp-2">
                                        {course.title}
                                    </h3>
                                    <p className="text-foreground/70 text-sm mb-4 flex-1 line-clamp-3">
                                        {course.description || "Chưa có mô tả"}
                                    </p>

                                    {/* Course info */}
                                    <div className="flex justify-between items-center text-sm text-foreground/60 mb-4">
                                        <span>⏱ {formatDuration(course.duration)}</span>
                                        <span className="px-2 py-1 bg-foreground/5 rounded-full">
                                            {course.tags || "Thuật toán"}
                                        </span>
                                    </div>

                                    {/* Button */}
                                    <div className="mt-auto">
                                        <button
                                            className="w-full py-2 px-4 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity"
                                            onClick={(e) => {
                                                e.stopPropagation(); // Prevent card click
                                                handleCourseClick(course.id);
                                            }}
                                        >
                                            {course.isEnrolled ? "Tiếp tục học" : "Xem chi tiết"}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex justify-center items-center gap-2 mt-12">
                            <button
                                onClick={() => handlePageChange(currentPage - 1)}
                                disabled={currentPage === 1}
                                className="px-4 py-2 rounded-lg border border-foreground/20 hover:bg-foreground/5 disabled:opacity-50 disabled:cursor-not-allowed transition"
                            >
                                ← Trước
                            </button>

                            {[...Array(totalPages)].map((_, i) => {
                                const page = i + 1;
                                return (
                                    <button
                                        key={page}
                                        onClick={() => handlePageChange(page)}
                                        className={`px-4 py-2 rounded-lg transition ${currentPage === page
                                            ? "bg-primary text-white"
                                            : "border border-foreground/20 hover:bg-foreground/5"
                                            }`}
                                    >
                                        {page}
                                    </button>
                                );
                            })}

                            <button
                                onClick={() => handlePageChange(currentPage + 1)}
                                disabled={currentPage === totalPages}
                                className="px-4 py-2 rounded-lg border border-foreground/20 hover:bg-foreground/5 disabled:opacity-50 disabled:cursor-not-allowed transition"
                            >
                                Tiếp →
                            </button>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}