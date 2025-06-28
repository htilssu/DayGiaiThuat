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
  lesson_id: number;
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
  external_id: string;
  title: string;
  description: string;
  topic_id: number;
  order: number;
  next_lesson_id?: string | null;
  prev_lesson_id?: string | null;
  sections: LessonSection[];
  exercise?: Exercise | null;
}

/**
 * Kiểu dữ liệu cho chủ đề
 */
export interface Topic {
  id: number;
  name: string;
  description?: string | null;
  prerequisites?: string[] | null;
  external_id?: string | null;
  course_id: number;
}

/**
 * Kiểu dữ liệu cho chủ đề bao gồm danh sách bài học
 */
export interface TopicWithLessons extends Topic {
  lessons: Lesson[];
}
