import Link from "next/link";

export default function LessonNotFound() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center px-4 py-16">
            <div className="text-center max-w-md">
                <div className="text-6xl font-bold text-primary mb-4">404</div>
                <h1 className="text-2xl font-bold mb-4">Bài học không tồn tại</h1>
                <p className="text-foreground/70 mb-8">
                    Bài học bạn đang tìm kiếm không tồn tại hoặc đã bị xóa. Vui lòng kiểm tra lại đường dẫn hoặc quay lại lộ trình học tập.
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                    <Link
                        href="/learn"
                        className="px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all"
                    >
                        Quay lại lộ trình
                    </Link>
                    <Link
                        href="/"
                        className="px-6 py-3 bg-background border border-primary text-primary font-semibold rounded-lg hover:bg-primary/5 transition-all"
                    >
                        Trang chủ
                    </Link>
                </div>
            </div>
        </div>
    );
} 