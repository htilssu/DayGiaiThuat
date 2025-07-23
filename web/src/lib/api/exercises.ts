/**
 * API client cho các thao tác với bài tập (exercises)
 * @module api/exercises
 */

import { get, post, put, del } from "./client";
import type { Exercise } from "./types";
import type { CodeSubmissionRequest, CodeSubmissionResponse } from "./types";

/**
 * Kiểu dữ liệu cho yêu cầu tạo bài tập
 */
export interface CreateExerciseRequest {
  lesson_id: number;
  session_id: string;
  difficulty: string;
  topic_id: number;
}

/**
 * Kiểu dữ liệu cho yêu cầu gửi code đến Judge0
 */
export interface Judge0SubmissionRequest {
  code: string;
  language: string;
  stdin?: string;
}

/**
 * Kiểu dữ liệu cho phản hồi từ Judge0
 */
export interface Judge0SubmissionResponse {
  token: string;
  stdout?: string;
  stderr?: string;
  compile_output?: string;
  message?: string;
  status: {
    id: number;
    description: string;
  };
}

/**
 * Lấy bài tập theo ID
 * @param id - ID của bài tập
 * @returns Thông tin bài tập
 */
async function getExerciseById(id: number) {
  return get<Exercise>(`/exercise/${id}`);
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
 * Cập nhật bài tập
 * @param id - ID của bài tập
 * @param exerciseData - Dữ liệu cập nhật
 * @returns Thông tin bài tập đã cập nhật
 */
async function updateExercise(id: number, exerciseData: Partial<Exercise>) {
  return put<Exercise>(`/exercise/${id}`, exerciseData);
}

/**
 * Xóa bài tập
 * @param id - ID của bài tập
 * @returns Kết quả xóa
 */
async function deleteExercise(id: number) {
  return del(`/exercise/${id}`);
}

/**
 * Nộp code cho bài tập và nhận kết quả test case
 * @param exerciseId - ID của bài tập
 * @param submission - Code và ngôn ngữ
 * @returns Kết quả chấm từng test case
 */
async function submitExerciseCode(
  exerciseId: number,
  submission: CodeSubmissionRequest
) {
  return post<CodeSubmissionResponse>(
    `/exercise/${exerciseId}/submit`,
    submission
  );
}

/**
 * Gửi code đến backend để chấm qua Judge0 và nhận kết quả
 * @param exerciseId - ID của bài tập
 * @param submission - Code, ngôn ngữ
 * @returns Kết quả chấm từng test case từ backend
 */
async function sendCodeToJudge(
  exerciseId: number,
  submission: CodeSubmissionRequest
): Promise<CodeSubmissionResponse> {
  return post<CodeSubmissionResponse>(
    `/exercise/${exerciseId}/judge0-submit`,
    submission
  );
}

export const exercisesApi = {
  getExerciseById,
  createExercise,
  updateExercise,
  deleteExercise,
  submitExerciseCode,
  sendCodeToJudge,
};
