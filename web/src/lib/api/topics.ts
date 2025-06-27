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
    external_id: string;
    title: string;
    description: string;
    topic_id: number;
    order: number;
    next_lesson_id?: string;
    prev_lesson_id?: string;
    sections?: Array<{
        id: number;
        type: string;
        content: string;
        order: number;
        options?: any;
        answer?: number;
        explanation?: string;
    }>;
    is_completed?: boolean;
    progress?: number;
    last_section_index?: number;
    completed_at?: string;
}



export async function getTopicLessons(topicId: number): Promise<Lesson[]> {
    return get<Lesson[]>(`/topics/${topicId}/lessons`);
}

/**
 * Lấy danh sách topics của khóa học kèm theo lessons
 * @param courseId ID của khóa học
 * @returns Danh sách topics với lessons
 */
export async function getTopicsWithLessons(courseId: number): Promise<Array<Topic & { lessons: Lesson[] }>> {
    const topics = await getTopicsByCourse(courseId);

    // Lấy lessons cho từng topic
    const topicsWithLessons = await Promise.all(
        topics.map(async (topic) => {
            const lessons = await getTopicLessons(topic.id);
            return {
                ...topic,
                lessons
            };
        })
    );

    return topicsWithLessons;
}

export async function getLessonById(lessonId: number): Promise<Lesson> {
    return get<Lesson>(`/lessons/${lessonId}`);
}

export async function markLessonCompleted(lessonId: number): Promise<any> {
    // Giả lập delay của API call
    await new Promise(resolve => setTimeout(resolve, 300));

    // Giả lập thành công
    return { success: true, message: "Lesson marked as completed" };
} 