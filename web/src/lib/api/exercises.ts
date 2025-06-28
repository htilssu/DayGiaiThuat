/**
 * API client cho các thao tác với bài tập (exercises)
 * @module api/exercises
 */

import { get, post, put, del } from "./client";
import type { Exercise } from "./types";

/**
 * Kiểu dữ liệu cho yêu cầu tạo bài tập
 */
export interface CreateExerciseRequest {
  lesson_id: number;
  session_id: string;
  difficulty: string;
}

/**
 * Lấy thông tin chi tiết của một bài tập theo ID
 * @param exerciseId - ID của bài tập
 * @returns Thông tin chi tiết bài tập
 */
async function getExerciseById(exerciseId: number) {
  return get<Exercise>(`/exercise/${exerciseId}`);
}

/**
 * Tạo mới một bài tập
 * @param exerciseData - Dữ liệu bài tập mới
 * @returns Thông tin bài tập đã tạo
 */
async function createExercise(exerciseData: CreateExerciseRequest) {
  return post<Exercise>(`/exercise/create`, exerciseData);
}

/**
 * Cập nhật thông tin bài tập
 * @param exerciseId - ID của bài tập
 * @param exerciseData - Dữ liệu cập nhật
 * @returns Thông tin bài tập đã cập nhật
 */
async function updateExercise(
  exerciseId: number,
  exerciseData: Partial<CreateExerciseRequest>
) {
  return put<Exercise>(`/exercise/${exerciseId}`, exerciseData);
}

/**
 * Xóa một bài tập
 * @param exerciseId - ID của bài tập
 * @returns Kết quả xóa
 */
async function deleteExercise(exerciseId: number) {
  return del<{ message: string }>(`/exercise/${exerciseId}`);
}

export const exercisesApi = {
  getExerciseById,
  createExercise,
  updateExercise,
  deleteExercise,
};
