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
 * Gửi code đến Judge0 để chấm điểm
 * @param {Object} params
 * @param {string} params.code - Source code
 * @param {string} params.language - Language id or name
 * @param {string} [params.stdin] - Optional input
 * @returns {Promise<any>} Judge0 API response
 */
export async function sendCodeToJudge({
  code,
  language,
  stdin,
}: {
  code: string;
  language: string;
  stdin?: string;
}) {
  // Map language name to Judge0 language_id if needed
  // For demo, assume language is already Judge0's language_id
  const body = {
    source_code: code,
    language_id: language, // You may need to map this
    stdin: stdin || "",
  };

  const res = await fetch(
    "https://judge0-extra-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-RapidAPI-Host": "judge0-extra-ce.p.rapidapi.com",
        "X-RapidAPI-Key": "d9adf119c4msh9041921e62d6d88p1eadeejsn847675e333d6",
      },
      body: JSON.stringify(body),
    }
  );
  if (!res.ok) {
    throw new Error("Failed to send code to Judge0");
  }
  return res.json();
}

export const exercisesApi = {
  getExerciseById,
  createExercise,
  updateExercise,
  deleteExercise,
  submitExerciseCode,
};
