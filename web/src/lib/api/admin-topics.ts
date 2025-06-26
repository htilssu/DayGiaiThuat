/**
 * API client cho admin quản lý chủ đề
 * @module api/admin-topics
 */

import { get, post, del, put } from "./client";

/**
 * Kiểu dữ liệu cho chủ đề
 */
export interface Topic {
    id: number;
    name: string;
    description: string | null;
    courseId: number;
    createdAt: string;
    updatedAt: string;
}

export type TopicCreatePayload = Omit<Topic, "id" | "createdAt" | "updatedAt">;
export type TopicUpdatePayload = Partial<Pick<Topic, "name" | "description">>;

/**
 * Lấy tất cả chủ đề (admin)
 * @returns Danh sách tất cả chủ đề
 */
export async function getAllTopicsAdmin(): Promise<Topic[]> {
    return get<Topic[]>("/admin/topics");
}

/**
 * Lấy danh sách chủ đề theo khóa học (admin)
 * @param courseId ID của khóa học
 * @returns Danh sách chủ đề
 */
export async function getTopicsByCourseAdmin(courseId: number): Promise<Topic[]> {
    return get<Topic[]>(`/admin/topics?course_id=${courseId}`);
}

/**
 * Lấy thông tin chi tiết của một chủ đề (admin)
 * @param id ID của chủ đề
 * @returns Thông tin chi tiết chủ đề
 */
export async function getTopicByIdAdmin(id: number): Promise<Topic> {
    return get<Topic>(`/admin/topics/${id}`);
}

/**
 * Tạo chủ đề mới (admin)
 * @param topicData Dữ liệu chủ đề mới
 * @returns Chủ đề vừa được tạo
 */
export async function createTopicAdmin(topicData: TopicCreatePayload): Promise<Topic> {
    return post<Topic>("/admin/topics", topicData);
}

/**
 * Cập nhật chủ đề (admin)
 * @param id ID của chủ đề
 * @param topicData Dữ liệu cập nhật
 * @returns Chủ đề sau khi cập nhật
 */
export async function updateTopicAdmin(id: number, topicData: TopicUpdatePayload): Promise<Topic> {
    return put<Topic>(`/admin/topics/${id}`, topicData);
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
    deleteTopicAdmin,
}; 