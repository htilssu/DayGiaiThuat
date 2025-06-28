/**
 * Shared types for API modules
 * @module api/types
 */

/**
 * Kiểu dữ liệu cho bài tập
 */
export interface Exercise {
  id: number;
  name: string;
  description: string;
  difficulty: string;
  constraint?: string;
  suggest?: string;
  lessonId: number;
}

/**
 * Kiểu dữ liệu cho phần nội dung bài học
 */
export interface LessonSection {
  type: string; // "text", "code", "image", "quiz"
  content: string;
  order: number;
  options?: Record<string, unknown> | null;
  answer?: number | null;
  explanation?: string | null;
}

/**
 * Kiểu dữ liệu cho bài học
 */
export interface Lesson {
  id: number;
  externalId: string;
  title: string;
  description: string;
  topicId: number;
  order: number;
  nextLessonId?: string | null;
  prevLessonId?: string | null;
  sections: LessonSection[];
  exercise?: Exercise | null;
}

/**
 * Kiểu dữ liệu cho chủ đề
 */

