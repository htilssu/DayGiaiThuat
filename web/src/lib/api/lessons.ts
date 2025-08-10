/**
 * API client cho các thao tác với bài học (lessons)
 * @module api/lessons
 */

import { get, post, put, del } from "./client";

export interface LessonSection {
  id: number;
  title: string;
  content: string;
  options: Record<string, string>;
  answer: string;
  explanation: string;
  type: string;
  order: number;
}

export interface LessonCompleteResponseSchema {
  lessonId: number;
  nextLessonId: number | null;
  isCompleted: boolean;
}

export interface Lesson {
  id: number;
  externalId: string;
  title: string;
  description?: string;
  type: string;
  order: number;
  topicId: number;
  content?: string;
  sections?: LessonSection[];
  createdAt: string;
  updatedAt: string;
  isCompleted: boolean;
  nextLessonId: number | null;
  prevLessonId: number | null;
}

/**
 * Kiểu dữ liệu cho yêu cầu tạo bài học
 */
export interface CreateLessonRequest {
  externalId: string;
  title: string;
  description: string;
  topicId: number;
  order: number;
  nextLessonId?: string;
  prevLessonId?: string;
  sections: LessonSection[];
}

/**
 * Kiểu dữ liệu cho yêu cầu cập nhật bài học
 */
export interface UpdateLessonRequest {
  title?: string;
  description?: string;
  order?: number;
  nextLessonId?: string;
  prevLessonId?: string;
}

/**
 * Kiểu dữ liệu cho yêu cầu tạo bài học bằng AI
 */
export interface GenerateLessonRequest {
  topicName: string;
  lessonTitle: string;
  lessonDescription: string;
  difficultyLevel?: string; // "beginner", "intermediate", "advanced"
  lessonType?: string; // "theory", "practice", "mixed"
  includeExamples?: boolean;
  includeExercises?: boolean;
  maxSections?: number;
}

/**
 * Lấy thông tin chi tiết của một bài học theo ID
 * @param lessonId - ID của bài học
 * @returns Thông tin chi tiết bài học
 */
async function getLessonById(lessonId: number) {
  return get<Lesson>(`/lessons/${lessonId}`);
}

/**
 * Lấy thông tin chi tiết của một bài học theo external ID
 * @param externalId - External ID của bài học
 * @returns Thông tin chi tiết bài học
 */
async function getLessonByExternalId(externalId: string) {
  return get<Lesson>(`/lessons/external/${externalId}`);
}

/**
 * Lấy danh sách bài học theo chủ đề
 * @param topicId - ID của chủ đề
 * @returns Danh sách bài học
 */
async function getLessonsByTopic(topicId: number) {
  return get<Lesson[]>(`/lessons/topic/${topicId}`);
}

/**
 * Tạo mới một bài học
 * @param lessonData - Dữ liệu bài học mới
 * @returns Thông tin bài học đã tạo
 */
async function createLesson(lessonData: CreateLessonRequest) {
  return post<Lesson>(`/lessons`, lessonData);
}

/**
 * Tạo bài học bằng AI
 * @param topicId - ID của chủ đề
 * @param order - Thứ tự bài học
 * @param requestData - Dữ liệu yêu cầu tạo bài học
 * @returns Thông tin bài học đã tạo
 */
async function generateLesson(
  topicId: number,
  order: number,
  requestData: GenerateLessonRequest
) {
  return post<Lesson>(`/lessons/generate`, requestData, {
    params: { topicId, order },
  });
}

/**
 * Cập nhật thông tin bài học
 * @param lessonId - ID của bài học
 * @param lessonData - Dữ liệu cập nhật
 * @returns Thông tin bài học đã cập nhật
 */
async function updateLesson(lessonId: number, lessonData: UpdateLessonRequest) {
  return put<Lesson>(`/lessons/${lessonId}`, lessonData);
}

/**
 * Xóa một bài học
 * @param lessonId - ID của bài học
 * @returns Kết quả xóa
 */
async function deleteLesson(lessonId: number) {
  return del<{ message: string }>(`/lessons/${lessonId}`);
}

async function completeLesson(lessonId: number) {
  return post<LessonCompleteResponseSchema>(`/lessons/${lessonId}/complete`);
}

export const lessonsApi = {
  getLessonById,
  getLessonByExternalId,
  getLessonsByTopic,
  createLesson,
  generateLesson,
  updateLesson,
  deleteLesson,
  completeLesson,
};
