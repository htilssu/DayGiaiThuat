"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

/**
 * Redirect page cho khóa học đã đăng ký
 * Chuyển hướng người dùng đến trang chính hiển thị khóa học đã đăng ký tại /courses
 */
export default function EnrolledCoursesRedirectPage() {
    const router = useRouter();

    useEffect(() => {
        // Chuyển hướng ngay lập tức đến trang /courses
        router.replace("/courses");
    }, [router]);

    // Hiển thị loading trong thời gian chuyển hướng
    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-foreground/70">Đang chuyển hướng đến khóa học của bạn...</p>
            </div>
        </div>
    );
} 