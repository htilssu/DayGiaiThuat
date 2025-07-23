/**
 * API client cho các thao tác với bài tập (exercises)
 * @module api/exercises
 */

import { get, post, put, del } from "./client";

export interface CodeSubmissionRequest {
  code: string;
  language: string;
}

export interface TestCaseResult {
  input: string;
  expectedOutput: string;
  actualOutput: string;
  passed: boolean;
  error?: string | null;
}

export interface CodeSubmissionResponse {
  results: TestCaseResult[];
  allPassed: boolean;
}

/**
 * Kiểu dữ liệu cho yêu cầu tạo bài tập
 */
export interface CreateExerciseRequest {
  lessonId: number;
  sessionId: string;
  difficulty: string;
  topicId: number;
}

export interface Exercise {
  id: number;
  lessonId: number;
  sessionId: string;
  difficulty: string;
  topicId: number;
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
 * Gửi code đến Judge0 để chạy và nhận kết quả
 * @param submission - Code, ngôn ngữ và input
 * @returns Kết quả từ Judge0
 */

async function sendCodeToJudge(
  submission: Judge0SubmissionRequest
): Promise<Judge0SubmissionResponse> {
  const JUDGE0_API_URL = "https://3b947351b5b5.ngrok-free.app";

  function sleep(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  try {
    // Tạo submission
    const createResponse = await fetch(`${JUDGE0_API_URL}/submissions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        source_code: submission.code,
        language_id: getLanguageId(submission.language),
        stdin: submission.stdin || "",
      }),
    });

    if (!createResponse.ok) {
      throw new Error(
        `Failed to create submission: ${createResponse.statusText}`
      );
    }

    const createData = await createResponse.json();
    const token = createData.token;

    // Poll for result until status is 'Accepted'
    let resultData;
    while (true) {
      const resultResponse = await fetch(
        `${JUDGE0_API_URL}/submissions/${token}`,
        {
          method: "get",
          headers: new Headers({
            "ngrok-skip-browser-warning": "69420",
          }),
        }
      );
      resultData = await resultResponse.json();
      if (resultData.status && resultData.status.description === "Accepted") {
        break;
      }
      await sleep(500); // Wait 500ms before polling again
    }

    return resultData;
  } catch (error) {
    console.error("Judge0 API error:", error);
    throw error;
  }
}

/**
 * Map ngôn ngữ lập trình sang Judge0 language ID
 * @param language - Tên ngôn ngữ
 * @returns Judge0 language ID
 */
function getLanguageId(language: string): number {
  const languageMap: Record<string, number> = {
    javascript: 63, // Node.js
    typescript: 74, // TypeScript
    python: 71, // Python
    csharp: 51, // C#
    c: 50, // C
    cpp: 54, // C++
    java: 62, // Java
    php: 68, // PHP
    ruby: 72, // Ruby
    swift: 83, // Swift
  };

  return languageMap[language.toLowerCase()] || 63; // Default to JavaScript
}

export const exercisesApi = {
  getExerciseById,
  createExercise,
  updateExercise,
  deleteExercise,
  submitExerciseCode,
  sendCodeToJudge,
};
