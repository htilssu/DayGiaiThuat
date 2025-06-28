/**
 * API client cho admin quản lý chủ đề
 * @module api/admin-topics
 */

import { get, post, del, put, patch } from "./client";

/**
 * Kiểu dữ liệu cho chủ đề (Admin)
 */
export interface AdminTopic {
    id: number;
    name: string;
    description: string | null;
    courseId: number | null;
    createdAt: string;
    updatedAt: string;
}

export type AdminTopicCreatePayload = Omit<AdminTopic, "id" | "createdAt" | "updatedAt">;
export type AdminTopicUpdatePayload = Partial<Pick<AdminTopic, "name" | "description">>;
export type AdminTopicCourseAssignmentPayload = {
    courseId: number | null;
};

/**
 * Lấy tất cả chủ đề (admin)
 * @returns Danh sách tất cả chủ đề
 */
export async function getAllTopicsAdmin(): Promise<AdminTopic[]> {
    return get<AdminTopic[]>("/admin/topics");
}

/**
 * Lấy danh sách chủ đề theo khóa học (admin)
 * @param courseId ID của khóa học
 * @returns Danh sách chủ đề
 */
export async function getTopicsByCourseAdmin(courseId: number): Promise<AdminTopic[]> {
    return get<AdminTopic[]>(`/admin/topics?course_id=${courseId}`);
}

/**
 * Lấy thông tin chi tiết của một chủ đề (admin)
 * @param id ID của chủ đề
 * @returns Thông tin chi tiết chủ đề
 */
export async function getTopicByIdAdmin(id: number): Promise<AdminTopic> {
    return get<AdminTopic>(`/admin/topics/${id}`);
}

/**
 * Tạo chủ đề mới (admin)
 * @param topicData Dữ liệu chủ đề mới
 * @returns Chủ đề vừa được tạo
 */
export async function createTopicAdmin(topicData: AdminTopicCreatePayload): Promise<AdminTopic> {
    return post<AdminTopic>("/admin/topics", topicData);
}

/**
 * Cập nhật chủ đề (admin)
 * @param id ID của chủ đề
 * @param topicData Dữ liệu cập nhật
 * @returns Chủ đề sau khi cập nhật
 */
export async function updateTopicAdmin(id: number, topicData: AdminTopicUpdatePayload): Promise<AdminTopic> {
    return put<AdminTopic>(`/admin/topics/${id}`, topicData);
}

/**
 * Assign/Unassign chủ đề với khóa học (admin)
 * @param id ID của chủ đề
 * @param assignmentData Dữ liệu assign khóa học
 * @returns Chủ đề sau khi assign
 */
export async function assignTopicToCourseAdmin(id: number, assignmentData: AdminTopicCourseAssignmentPayload): Promise<AdminTopic> {
    return patch<AdminTopic>(`/admin/topics/${id}/assign-course`, {
        course_id: assignmentData.courseId
    });
}

/**
 * Xóa chủ đề (admin)
 * @param id ID của chủ đề cần xóa
 */
export async function deleteTopicAdmin(id: number): Promise<void> {
    return del(`/admin/topics/${id}`);
}

export const adminTopicsApi = {
    getAllTopicsAdmin,
    getTopicsByCourseAdmin,
    getTopicByIdAdmin,
    createTopicAdmin,
    updateTopicAdmin,
    assignTopicToCourseAdmin,
    deleteTopicAdmin,
}; 