import { get, post } from "./client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Topic {
    id: number;
    name: string;
    description: string;
    courseId: number;
    createdAt: string;
    updatedAt: string;
}

export type TopicCreatePayload = Omit<Topic, "id" | "createdAt" | "updatedAt">;

/**
 * Lấy danh sách chủ đề của một khóa học
 * @param courseId ID của khóa học
 * @returns Danh sách các chủ đề
 */
export async function getTopicsByCourse(courseId: number): Promise<Topic[]> {
    return get<Topic[]>(`/topics/`, { params: { courseId } });
}

/**
 * Tạo chủ đề mới
 * @param topicData Dữ liệu chủ đề mới
 * @returns Chủ đề vừa được tạo
 */
export async function createTopic(topicData: TopicCreatePayload): Promise<Topic> {
    return post<Topic>("/topics/", topicData);
}

export interface Lesson {
    id: number;
    title: string;
    description: string;
    content?: string;
    order: number;
    topic_id: number;
    is_completed?: boolean;
}

// Giữ lại các hàm liên quan đến Lesson vì chúng có thể vẫn hữu ích
// và chưa có router tương ứng ở backend.
const mockLessons: Record<number, Lesson[]> = {
    1: [
        {
            id: 1,
            title: "Giới thiệu tổng quan",
            description: "Tổng quan về khóa học và các mục tiêu",
            content: "# Giới thiệu tổng quan\n\nĐây là nội dung bài học về giới thiệu tổng quan...",
            order: 1,
            topic_id: 1,
            is_completed: true,
        },
        {
            id: 2,
            title: "Cài đặt môi trường",
            description: "Hướng dẫn cài đặt các công cụ cần thiết",
            content: "# Cài đặt môi trường\n\nĐây là nội dung bài học về cài đặt môi trường...",
            order: 2,
            topic_id: 1,
            is_completed: true,
        },
        {
            id: 3,
            title: "Kiến thức nền tảng",
            description: "Các kiến thức cơ bản cần biết trước khi bắt đầu",
            content: "# Kiến thức nền tảng\n\nĐây là nội dung bài học về kiến thức nền tảng...",
            order: 3,
            topic_id: 1,
            is_completed: false,
        },
    ],
    2: [
        {
            id: 4,
            title: "Mảng và danh sách liên kết",
            description: "Tìm hiểu về mảng và danh sách liên kết",
            content: "# Mảng và danh sách liên kết\n\nĐây là nội dung bài học về mảng và danh sách liên kết...",
            order: 1,
            topic_id: 2,
            is_completed: false,
        },
        {
            id: 5,
            title: "Ngăn xếp và hàng đợi",
            description: "Tìm hiểu về ngăn xếp và hàng đợi",
            content: "# Ngăn xếp và hàng đợi\n\nĐây là nội dung bài học về ngăn xếp và hàng đợi...",
            order: 2,
            topic_id: 2,
            is_completed: false,
        },
    ]
};

export async function getTopicLessons(topicId: number): Promise<Lesson[]> {
    // Giả lập delay của API call
    await new Promise(resolve => setTimeout(resolve, 300));

    const lessons = mockLessons[topicId];
    if (!lessons) {
        // Trả về mảng rỗng nếu không có bài học
        return [];
    }
    return lessons;
}

export async function getLessonById(lessonId: number): Promise<Lesson> {
    // Giả lập delay của API call
    await new Promise(resolve => setTimeout(resolve, 300));

    for (const topicLessons of Object.values(mockLessons)) {
        const lesson = topicLessons.find(l => l.id === lessonId);
        if (lesson) {
            return lesson;
        }
    }
    throw new Error(`Lesson with id ${lessonId} not found`);
}

export async function markLessonCompleted(lessonId: number): Promise<any> {
    // Giả lập delay của API call
    await new Promise(resolve => setTimeout(resolve, 300));

    // Giả lập thành công
    return { success: true, message: "Lesson marked as completed" };
} 