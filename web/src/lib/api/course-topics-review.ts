/**
 * API client cho review topics của khóa học
 */

import { get, post, put } from "./client";
import { CourseTopicsReview, UpdateTopicRequest } from "@/types/course-review";

/**
 * Lấy thông tin review topics của khóa học
 * @param courseId ID của khóa học
 * @returns Thông tin review topics
 */
export async function getCourseTopicsReview(courseId: number): Promise<CourseTopicsReview> {
    return get<CourseTopicsReview>(`/admin/courses/${courseId}/review`);
}

/**
 * Cập nhật thông tin topic
 * @param courseId ID của khóa học
 * @param topicId ID của topic
 * @param data Dữ liệu cập nhật
 * @returns Kết quả cập nhật
 */
export async function updateTopic(courseId: number, data: UpdateTopicRequest): Promise<{ success: boolean; message: string }> {
    return put<{ success: boolean; message: string }>(`/admin/topics/draft/${courseId}`, data);
}

/**
 * Thay đổi thứ tự các topics
 * @param courseId ID của khóa học  
 * @param data Dữ liệu topics đầy đủ với thứ tự mới
 * @returns Kết quả cập nhật
 */
export async function reorderTopics(courseId: number, data: UpdateTopicRequest): Promise<{ success: boolean; message: string }> {
    return put<{ success: boolean; message: string }>(`/admin/courses/${courseId}/topics/reorder`, data);
}


/**
 * Chấp nhận và chuyển sang bước tiếp theo (tạo lessons)
 * @param courseId ID của khóa học
 * @returns Kết quả xử lý
 */
export async function approveTopicsAndNext(courseId: number): Promise<{ success: boolean; message: string }> {
    return post<{ success: boolean; message: string }>(`/admin/courses/${courseId}/topic/approve`, {});
}

/**
 * Từ chối và yêu cầu tạo lại topics
 * @param courseId ID của khóa học
 * @param feedback Ý kiến phản hồi
 * @returns Kết quả xử lý
 */
export async function rejectTopicsAndRegenerate(courseId: number, feedback: string): Promise<{ success: boolean; message: string }> {
    return post<{ success: boolean; message: string }>(`/admin/courses/${courseId}/topic/reject`, { feedback });
}
