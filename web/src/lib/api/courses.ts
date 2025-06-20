/**
 * API client cho các thao tác với khóa học
 * @module api/courses
 */

import { get, post } from "./client";

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
  createdAt: string;
  updatedAt: string;
}

/**
 * Lấy danh sách khóa học có phân trang
 * @param page - Số trang
 * @param limit - Số lượng item mỗi trang
 * @returns Danh sách khóa học và thông tin phân trang
 */
async function getCourses(page = 1, limit = 10) {
  return get<{
    items: Course[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }>(`/courses`, { params: { page, limit } });
}

/**
 * Lấy thông tin chi tiết của một khóa học
 * @param id - ID của khóa học
 * @returns Thông tin chi tiết khóa học
 */
async function getCourseById(id: number) {
  return get<Course>(`/courses/${id}`);
}

/**
 * Đăng ký khóa học
 * @param courseId - ID của khóa học
 * @returns Thông tin đăng ký khóa học
 */
async function registerCourse(courseId: number) {
  return post<{ success: boolean; message: string }>(`/courses/${courseId}/register`);
}

export const coursesApi = {
  getCourses,
  getCourseById,
  registerCourse,
};

