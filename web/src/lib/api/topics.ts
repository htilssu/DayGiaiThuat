/**
 * API client cho các thao tác với chủ đề (topics)
 * @module api/topics
 */

import { get, post, put, del } from "./client";
import type { Lesson } from "./types";

export interface Topic {
  id: number;
  name: string;
  description?: string | null;
  prerequisites?: string[] | null;
  externalId?: string | null;
  courseId: number;
  createdAt?: string;
  updatedAt?: string;
}

/**
 * Lấy danh sách chủ đề theo khóa học
 * @param courseId - ID của khóa học
 * @returns Danh sách chủ đề
 */
async function getTopicsByCourse(courseId: number) {
  return get<Topic[]>(`/topics/course/${courseId}`);
}

/**
 * Lấy thông tin chi tiết của một chủ đề
 * @param topicId - ID của chủ đề
 * @returns Thông tin chi tiết chủ đề
 */
async function getTopicById(topicId: number) {
  return get<Topic>(`/topics/${topicId}`);
}

/**
 * Lấy thông tin chi tiết của một chủ đề bao gồm danh sách bài học
 * @param topicId - ID của chủ đề
 * @returns Thông tin chi tiết chủ đề với danh sách bài học
 */
async function getTopicWithLessons(topicId: number) {
  return get<Topic>(`/topics/${topicId}/with-lessons`);
}

/**
 * Cập nhật thông tin chủ đề
 * @param topicId - ID của chủ đề
 * @param topicData - Dữ liệu cập nhật
 * @returns Thông tin chủ đề đã cập nhật
 */
async function updateTopic(
  topicId: number,
  topicData: {
    name?: string;
    description?: string;
    prerequisites?: string[];
    external_id?: string;
  }
) {
  return put<Topic>(`/topics/${topicId}`, topicData);
}

/**
 * Xóa chủ đề
 * @param topicId - ID của chủ đề
 * @returns Kết quả xóa
 */
async function deleteTopic(topicId: number) {
  return del(`/topics/${topicId}`);
}

export type TopicCreatePayload = Omit<Topic, "id" | "createdAt" | "updatedAt">;

/**
 * Tạo chủ đề mới
 * @param topicData Dữ liệu chủ đề mới
 * @returns Chủ đề vừa được tạo
 */
export async function createTopic(topicData: TopicCreatePayload): Promise<Topic> {
  return post<Topic>("/topics", topicData);
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
  await new Promise(resolve => setTimeout(resolve, 300));

  return { success: true, message: "Lesson marked as completed" };
}

export const topicsApi = {
  getTopicsByCourse,
  getTopicById,
  getTopicWithLessons,
  createTopic,
  updateTopic,
  deleteTopic,
};
