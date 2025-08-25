import { Metadata } from "next";

interface ReviewLessonsPageProps {
    params: Promise<{
        id: string;
    }>;
}

export async function generateMetadata({ params }: ReviewLessonsPageProps): Promise<Metadata> {
    const { id } = await params;
    return {
        title: `Review Lessons - Khóa học ${id} - AI Agent Giải Thuật`,
        description: `Review và chỉnh sửa lessons cho khóa học ${id}`,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["review", "lessons", "bài học", "khóa học", "admin"],
    };
}

export default async function ReviewLessonsPage({ params }: ReviewLessonsPageProps) {
    const { id } = await params;

    // Placeholder component - sẽ được implement sau
    return (
        <div className="container mx-auto py-8">
            <h1 className="text-2xl font-bold mb-4">Review Lessons - Khóa học {id}</h1>
            <p className="text-muted-foreground">
                Trang review lessons đang được phát triển.
            </p>
        </div>
    );
}
