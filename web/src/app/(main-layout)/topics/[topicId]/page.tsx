import { Metadata } from "next";
import { notFound } from "next/navigation";
import { sampleLessons } from "@/components/pages/learn/sampleLessonData";
import TopicClient from "./components/TopicClient";

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

    return <TopicClient topicId={topicId} topic={topic} lessons={lessons} />;
} 