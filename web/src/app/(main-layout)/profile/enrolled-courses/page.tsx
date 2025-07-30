"use client";

import { useEffect, useState } from "react";
import { coursesApi, UserCourseDetail } from "@/lib/api";
import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";

export default function EnrolledCoursesPage() {
    const router = useRouter();
    const [courses, setCourses] = useState<UserCourseDetail[]>([]);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchEnrolledCourses = async () => {
            try {
                setIsLoading(true);
                const data = await coursesApi.getEnrolledCourses();
                setCourses(data);
            } catch (err) {
                console.error("Lỗi khi tải danh sách khóa học đã đăng ký:", err);
                setError("Không thể tải danh sách khóa học đã đăng ký. Vui lòng thử lại sau.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchEnrolledCourses();
    }, []);

    // Chuyển đổi phút thành định dạng giờ:phút
    const formatDuration = (minutes: number) => {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours > 0 ? `${hours} giờ ` : ""}${mins > 0 ? `${mins} phút` : ""}`;
    };

    if (isLoading) {
        return (
            <div className="py-10 px-4">
                <div className="max-w-6xl mx-auto">
                    <h1 className="text-3xl font-bold mb-8">Khóa học của bạn</h1>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="bg-foreground/5 rounded-xl overflow-hidden animate-pulse">
                                <div className="h-40 bg-foreground/10"></div>
                                <div className="p-4">
                                    <div className="h-6 bg-foreground/10 rounded w-3/4 mb-3"></div>
                                    <div className="h-4 bg-foreground/10 rounded w-1/2"></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="py-10 px-4">
                <div className="max-w-6xl mx-auto">
                    <h1 className="text-3xl font-bold mb-8">Khóa học của bạn</h1>
                    <div className="bg-foreground/5 rounded-xl p-10 text-center">
                        <h2 className="text-2xl font-bold mb-4 text-accent">{error}</h2>
                        <button
                            onClick={() => window.location.reload()}
                            className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
                            Thử lại
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    if (courses.length === 0) {
        return (
            <div className="py-10 px-4">
                <div className="max-w-6xl mx-auto">
                    <h1 className="text-3xl font-bold mb-8">Khóa học của bạn</h1>
                    <div className="bg-foreground/5 rounded-xl p-10 text-center">
                        <h2 className="text-2xl font-bold mb-4">Bạn chưa đăng ký khóa học nào</h2>
                        <p className="mb-6 text-foreground/70">
                            Khám phá các khóa học của chúng tôi và bắt đầu hành trình học tập của bạn ngay hôm nay.
                        </p>
                        <Link
                            href="/courses"
                            className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
                            Khám phá khóa học
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="py-10 px-4">
            <div className="max-w-6xl mx-auto">
                <h1 className="text-3xl font-bold mb-8">Khóa học của bạn</h1>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {courses.map((course) => (
                        <div
                            key={course.id}
                            className="bg-foreground/5 hover:bg-foreground/10 transition rounded-xl overflow-hidden cursor-pointer"
                            onClick={() => router.push(`/courses/${course.id}`)}>
                            <div className="relative h-40">
                                {course.thumbnailUrl ? (
                                    <Image
                                        src={course.thumbnailUrl}
                                        alt={course.title}
                                        fill
                                        className="object-cover"
                                    />
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center bg-primary/10">
                                        <span className="text-primary text-lg font-medium">
                                            {course.title.substring(0, 2).toUpperCase()}
                                        </span>
                                    </div>
                                )}
                                <div className="absolute top-2 right-2 bg-primary/90 text-white text-xs font-medium py-1 px-2 rounded">
                                    {course.level}
                                </div>
                            </div>
                            <div className="p-4">
                                <h3 className="font-bold text-lg mb-2 line-clamp-2">{course.title}</h3>
                                <div className="flex items-center text-sm text-foreground/70 mb-3">
                                    <svg
                                        xmlns="http://www.w3.org/2000/svg"
                                        className="h-4 w-4 mr-1"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor">
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                                        />
                                    </svg>
                                    <span>{formatDuration(course.duration)}</span>
                                </div>
                                <div className="flex justify-between items-center">
                                    <Link
                                        href={`/topics/${course.id}`}
                                        className="text-primary font-medium hover:underline"
                                        onClick={(e) => e.stopPropagation()}>
                                        Tiếp tục học
                                    </Link>
                                    {course.price > 0 ? (
                                        <span className="font-medium">
                                            {course.price.toLocaleString("vi-VN")}₫
                                        </span>
                                    ) : (
                                        <span className="text-green-600 font-medium">Miễn phí</span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
} 