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
  title?: string;
  name?: string;
  description: string;
  category?: string | null;
  difficulty: string;
  estimatedTime?: string | null;
  completionRate?: number | null;
  completed?: boolean | null;
  content?: string | null;
  codeTemplate?: string | null;
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
  compileOutput?: string;
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

async function listExercises(page = 1, limit = 12) {
  return get<Exercise[]>(`/exercise?page=${page}&limit=${limit}`);
}

/**
 * Lấy danh sách test case của một bài tập
 */
async function getExerciseTestCases(exerciseId: number) {
  return get<
    Array<{
      id: number;
      exercise_id: number;
      input_data: string;
      output_data: string;
      explain?: string | null;
    }>
  >(`/exercise/${exerciseId}/test-cases`);
}

/**
 * Lấy chi tiết bài tập kèm test cases và map sang cấu trúc UI
 */
type BackendExercise = {
  id: number;
  title?: string;
  name?: string;
  description: string;
  category?: string | null;
  difficulty: string;
  estimatedTime?: string | null;
  completionRate?: number | null;
  completed?: boolean | null;
  content?: string | null;
  codeTemplate?: string | null;
};

type BackendTestCase = {
  id: number;
  exercise_id: number;
  input_data: string;
  output_data: string;
  explain?: string | null;
};

type UiExerciseDetail = {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  estimatedTime: string;
  completionRate: number;
  completed: boolean;
  content: string;
  codeTemplate: string;
  testCases: Array<{ input: string; expectedOutput: string }>;
};

async function getExerciseDetailForUi(
  exerciseId: number
): Promise<UiExerciseDetail> {
  const [exercise, testCases] = await Promise.all([
    getExerciseById(exerciseId) as unknown as Promise<BackendExercise>,
    getExerciseTestCases(exerciseId) as Promise<BackendTestCase[]>,
  ]);

  const difficultyMap: Record<
    string,
    "Beginner" | "Intermediate" | "Advanced"
  > = {
    beginner: "Beginner",
    intermediate: "Intermediate",
    advanced: "Advanced",
  };

  const difficultyRaw = (exercise.difficulty as string) || "medium";
  const difficultyKey = String(difficultyRaw).toLowerCase();
  const difficulty = difficultyMap[difficultyKey] || "Intermediate";

  const testCasesUi = (testCases || []).map((tc) => ({
    input: tc.input_data,
    expectedOutput: tc.output_data,
  }));

  const codeTemplate = `function yourFunction(input) {
  // TODO: implement
  return input;
}`;

  return {
    id: exercise.id,
    title: exercise.title || exercise.name || "",
    description: exercise.description || "",
    category: exercise.category || "Thuật toán",
    difficulty,
    estimatedTime: exercise.estimatedTime || "",
    completionRate: exercise.completionRate || 0,
    completed: exercise.completed || false,
    content: exercise.content || exercise.description || "",
    codeTemplate: exercise.codeTemplate || codeTemplate,
    testCases: testCasesUi,
  };
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
  listExercises,
  getExerciseTestCases,
  getExerciseDetailForUi,
  createExercise,
  updateExercise,
  deleteExercise,
  submitExerciseCode,
  sendCodeToJudge,
};
