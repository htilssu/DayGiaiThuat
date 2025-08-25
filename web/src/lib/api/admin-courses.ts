/**
 * API client cho admin quản lý khóa học
 * @module api/admin-courses
 */

import { get, post, del, put } from "./client";

/**
 * Kiểu dữ liệu cho khóa học
 */
export interface Course {
    id: number;
    title: string;
    description: string | null;
    thumbnailUrl: string | null;
    level: string;
    duration: number;
    price: number;
    isPublished: boolean;
    tags: string;
    requirements: string | null;
    whatYouWillLearn: string | null;
    testGenerationStatus: string;
    createdAt: string;
    updatedAt: string;
}

export type CourseCreatePayload = Omit<Course, "id" | "createdAt" | "updatedAt" | "thumbnailUrl" | "testGenerationStatus"> & { thumbnailUrl?: string };
export type CourseUpdatePayload = Partial<CourseCreatePayload>;

/**
 * Kiểu dữ liệu cho request xóa nhiều khóa học
 */
export interface BulkDeleteCoursesRequest {
    courseIds: number[];
}

/**
 * Kiểu dữ liệu cho response xóa nhiều khóa học
 */
export interface BulkDeleteCoursesResponse {
    deletedCount: number;
    failedCount: number;
    errors: string[];
    deletedCourses: number[];
    failedCourses: number[];
}

/**
 * Kiểu dữ liệu cho request tạo topics với AI
 */
export interface GenerateTopicsRequest {
    title: string;
    description: string;
    level: string;
    maxTopics?: number;
}

/**
 * Kiểu dữ liệu cho skill trong topic
 */
export interface TopicSkill {
    description: string;
}

/**
 * Kiểu dữ liệu cho topic được generate
 */
export interface GeneratedTopic {
    name: string;
    description: string;
    prerequisites: string[];
    skills: string[];
    order: number;
}

/**
 * Kiểu dữ liệu cho response generate topics
 */
export interface GenerateTopicsResponse {
    status: string;
    topics: GeneratedTopic[];
    duration: string;
    courseId?: number;
    message: string;
}

/**
 * Lấy tất cả khóa học (admin) - bao gồm cả chưa published
 * @returns Danh sách tất cả khóa học
 */
export async function getAllCoursesAdmin(): Promise<Course[]> {
    return get<Course[]>("/admin/courses");
}

/**
 * Lấy thông tin chi tiết của một khóa học (admin)
 * @param id - ID của khóa học
 * @returns Thông tin chi tiết khóa học
 */
export async function getCourseByIdAdmin(id: number): Promise<Course> {
    return get<Course>(`/admin/courses/${id}`);
}

/**
 * Tạo khóa học mới (admin)
 * @param courseData Dữ liệu khóa học mới
 * @returns Khóa học vừa được tạo
 */
export async function createCourseAdmin(courseData: CourseCreatePayload): Promise<Course> {
    return post<Course>("/admin/courses", courseData);
}

/**
 * Cập nhật khóa học (admin)
 * @param id ID của khóa học
 * @param courseData Dữ liệu cập nhật
 * @returns Khóa học sau khi cập nhật
 */
export async function updateCourseAdmin(id: number, courseData: CourseUpdatePayload): Promise<Course> {
    return put<Course>(`/admin/courses/${id}`, courseData);
}

/**
 * Xóa khóa học (admin)
 * @param id ID của khóa học cần xóa
 */
export async function deleteCourseAdmin(id: number): Promise<void> {
    return del(`/admin/courses/${id}`);
}

/**
 * Xóa nhiều khóa học cùng lúc (admin)
 * @param courseIds Danh sách ID các khóa học cần xóa
 * @returns Kết quả xóa nhiều khóa học
 */
export async function bulkDeleteCoursesAdmin(courseIds: number[]): Promise<BulkDeleteCoursesResponse> {
    const request: BulkDeleteCoursesRequest = { courseIds };
    return del<BulkDeleteCoursesResponse>("/admin/courses/bulk", request);
}

/**
 * Tạo bài kiểm tra đầu vào cho khóa học (admin)
 * @param courseId ID của khóa học
 * @returns Kết quả tạo test
 */
export async function createCourseTestAdmin(courseId: number) {
    return post(`/admin/courses/${courseId}/test`);
}

/**
 * Generate topics cho khóa học bằng AI (admin)
 * @param request Thông tin khóa học để generate topics
 * @returns Danh sách topics được generate bởi AI
 */
export async function generateCourseTopics(request: GenerateTopicsRequest): Promise<GenerateTopicsResponse> {
    return post<GenerateTopicsResponse>("/admin/courses/generate-topics", request);
}

/**
 * Kiểu dữ liệu cho thông tin review khóa học
 */
export interface CourseReview {
    courseId: number;
    courseTitle: string;
    courseDescription: string;
    draft: {
        id: number;
        courseId: number;
        agentContent: string; // JSON string chứa topics, lessons
        sessionId: string;
        status: string;
        createdAt: string;
        updatedAt: string;
    } | null;
    chatMessages: Array<{
        id: number;
        courseId: number;
        userId: number;
        message: string;
        isAgent: boolean;
        createdAt: string;
    }>;
}

/**
 * Kiểu dữ liệu cho tin nhắn chat review
 */
export interface ReviewChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

/**
 * Kiểu dữ liệu cho request gửi tin nhắn chat review
 */
export interface ReviewChatRequest {
    message: string;
    context?: {
        courseData?: any;
        generatedContent?: any;
    };
}

/**
 * Kiểu dữ liệu cho response chat review
 */
export interface ReviewChatResponse {
    message: ReviewChatMessage;
    updatedContent?: any;
}

/**
 * Kiểu dữ liệu cho request approve/reject
 */
export interface ReviewApprovalRequest {
    approved: boolean;
    feedback?: string;
}

/**
 * Lấy thông tin review khóa học
 * @param courseId ID của khóa học
 * @returns Thông tin review khóa học
 */
export async function getCourseReview(courseId: number): Promise<CourseReview> {
    return get<CourseReview>(`/admin/courses/${courseId}/review`);
}

/**
 * Gửi tin nhắn chat với agent review
 * @param courseId ID của khóa học
 * @param request Dữ liệu tin nhắn chat
 * @returns Response từ AI agent
 */
export async function sendReviewChatMessage(courseId: number, request: ReviewChatRequest): Promise<ReviewChatResponse> {
    return post<ReviewChatResponse>(`/admin/courses/${courseId}/review/chat`, request);
}

/**
 * Approve hoặc reject draft khóa học
 * @param courseId ID của khóa học
 * @param request Dữ liệu approve/reject
 * @returns Kết quả xử lý
 */
export async function approveRejectCourse(courseId: number, request: ReviewApprovalRequest): Promise<{ success: boolean; message: string; }> {
    return post<{ success: boolean; message: string; }>(`/admin/courses/${courseId}/review/approve`, request);
}

async function forceDeleteCourse(courseId: number) {
    return del(`/admin/courses/${courseId}?force=1`)
}

export const adminCoursesApi = {
    getAllCoursesAdmin,
    getCourseByIdAdmin,
    createCourseAdmin,
    updateCourseAdmin,
    deleteCourseAdmin,
    bulkDeleteCoursesAdmin,
    createCourseTestAdmin,
    generateCourseTopics,
    getCourseReview,
    sendReviewChatMessage,
    approveRejectCourse,
    forceDeleteCourse
}; 