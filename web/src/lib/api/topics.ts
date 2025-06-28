/**
 * API client cho các thao tác với chủ đề (topics)
 * @module api/topics
 */

import { get, post, put, del } from "./client";
import type { Topic, TopicWithLessons } from "./types";

// Re-export types for convenience
export type { Topic, TopicWithLessons } from "./types";

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
  return get<TopicWithLessons>(`/topics/${topicId}/with-lessons`);
}

/**
 * Tạo mới một chủ đề
 * @param topicData - Dữ liệu chủ đề mới
 * @returns Thông tin chủ đề đã tạo
 */
async function createTopic(topicData: {
  name: string;
  description?: string;
  prerequisites?: string[];
  course_id: number;
  external_id?: string;
}) {
  return post<Topic>(`/topics`, topicData);
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
 * Xóa một chủ đề
 * @param topicId - ID của chủ đề
 * @returns Kết quả xóa
 */
async function deleteTopic(topicId: number) {
  return del<{ message: string }>(`/topics/${topicId}`);
}

export const topicsApi = {
  getTopicsByCourse,
  getTopicById,
  getTopicWithLessons,
  createTopic,
  updateTopic,
  deleteTopic,
};
