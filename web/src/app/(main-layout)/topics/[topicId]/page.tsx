import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { sampleLessons } from "@/components/pages/learn/sampleLessonData";

interface TopicPageProps {
    params: {
        topicId: string;
    };
}

// Dữ liệu mẫu cho các chủ đề
const topicsData = {
    "algorithms-basics": {
        title: "Cơ bản về giải thuật",
        description: "Tìm hiểu về các khái niệm cơ bản, độ phức tạp và cách phân tích giải thuật",
        color: "primary",
        icon: "📊"
    },
    "data-structures": {
        title: "Cấu trúc dữ liệu",
        description: "Học về các cấu trúc dữ liệu phổ biến như mảng, danh sách liên kết, ngăn xếp, hàng đợi",
        color: "secondary",
        icon: "🧩"
    },
    "sorting-algorithms": {
        title: "Giải thuật sắp xếp",
        description: "Tìm hiểu về các thuật toán sắp xếp như Bubble Sort, Quick Sort, Merge Sort và nhiều thuật toán khác",
        color: "accent",
        icon: "🔄"
    }
};

// Tạo metadata động dựa trên thông tin chủ đề
export async function generateMetadata({ params }: TopicPageProps): Promise<Metadata> {
    const { topicId } = params;
    const topic = topicsData[topicId as keyof typeof topicsData];

    if (!topic) {
        return {
            title: "Không tìm thấy chủ đề | AI Agent Giải Thuật",
            description: "Chủ đề không tồn tại hoặc đã bị xóa",
        };
    }

    return {
        title: `${topic.title} | AI Agent Giải Thuật`,
        description: topic.description,
        authors: [{ name: "AI Agent Giải Thuật Team" }],
        keywords: ["giải thuật", "học tập", "lập trình", "chủ đề", topic.title],
    };
}

export default function TopicPage({ params }: TopicPageProps) {
    const { topicId } = params;
    const topic = topicsData[topicId as keyof typeof topicsData];

    if (!topic) {
        notFound();
    }

    // Lấy danh sách bài học của chủ đề
    const topicLessons = sampleLessons[topicId] || {};
    const lessons = Object.values(topicLessons).sort((a, b) => parseInt(a.id) - parseInt(b.id));

    return (
        <div className="min-h-screen pb-20">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-10">
                    <Link href="/learn" className="text-primary hover:underline mb-2 inline-block">
                        ← Quay lại lộ trình
                    </Link>
                    <div className="flex items-center gap-4 mb-4">
                        <div className={`w-16 h-16 rounded-full flex items-center justify-center bg-${topic.color} text-white text-2xl`}>
                            {topic.icon}
                        </div>
                        <div>
                            <h1 className="text-3xl md:text-4xl font-bold">{topic.title}</h1>
                            <p className="text-foreground/70">{topic.description}</p>
                        </div>
                    </div>
                </div>

                {/* Danh sách bài học */}
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-2xl font-bold mb-6">Các bài học trong chủ đề này</h2>

                    <div className="space-y-4">
                        {lessons.length > 0 ? (
                            lessons.map((lesson) => (
                                <Link
                                    key={lesson.id}
                                    href={`/topics/${topicId}/lessons/${lesson.id}`}
                                    className="block bg-white rounded-xl p-6 shadow-sm border border-foreground/10 hover:shadow-md transition-all"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`w-10 h-10 rounded-full flex items-center justify-center bg-${topic.color} text-white font-bold`}>
                                            {lesson.id}
                                        </div>
                                        <div>
                                            <h3 className="text-xl font-semibold">{lesson.title}</h3>
                                            <p className="text-foreground/70">{lesson.description}</p>
                                        </div>
                                    </div>
                                </Link>
                            ))
                        ) : (
                            <div className="text-center py-10 bg-foreground/5 rounded-lg">
                                <p className="text-foreground/70">Chưa có bài học nào trong chủ đề này</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
} 