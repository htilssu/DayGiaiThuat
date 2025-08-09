/**
 * API client cho các thao tác với quiz
 * @module api/quizzes
 */

import { get, post, put, del } from "./client";

/**
 * Kiểu dữ liệu cho quiz
 */
export interface Quiz {
  id: number;
  lessonId: number;
  title: string;
  description: string;
  questions: QuizQuestion[];
  createdAt: string;
  updatedAt: string;
}

/**
 * Kiểu dữ liệu cho câu hỏi quiz
 */
export interface QuizQuestion {
  id: number;
  quizId: number;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation?: string;
  order: number;
}

/**
 * Kiểu dữ liệu cho yêu cầu tạo quiz
 */
export interface CreateQuizRequest {
  lessonId: number;
  questionCount: number;
  difficulty: string;
}

/**
 * Lấy thông tin chi tiết của một quiz theo ID
 * @param quizId - ID của quiz
 * @returns Thông tin chi tiết quiz
 */
async function getQuizById(quizId: number) {
  return get<Quiz>(`/quiz/${quizId}`);
}

/**
 * Tạo mới một quiz
 * @param quizData - Dữ liệu quiz mới
 * @returns Thông tin quiz đã tạo
 */
async function createQuiz(quizData: CreateQuizRequest) {
  return post<Quiz>(`/quiz/create`, quizData);
}

/**
 * Cập nhật thông tin quiz
 * @param quizId - ID của quiz
 * @param quizData - Dữ liệu cập nhật
 * @returns Thông tin quiz đã cập nhật
 */
async function updateQuiz(
  quizId: number,
  quizData: Partial<CreateQuizRequest>
) {
  return put<Quiz>(`/quiz/${quizId}`, quizData);
}

/**
 * Xóa một quiz
 * @param quizId - ID của quiz
 * @returns Kết quả xóa
 */
async function deleteQuiz(quizId: number) {
  return del<{ message: string }>(`/quiz/${quizId}`);
}

export const quizzesApi = {
  getQuizById,
  createQuiz,
  updateQuiz,
  deleteQuiz,
};
