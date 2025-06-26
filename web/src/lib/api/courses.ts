/**
 * API client cho các thao tác với khóa học
 * @module api/courses
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
  createdAt: string;
  updatedAt: string;
  isEnrolled?: boolean;
}

export type CourseCreatePayload = Omit<Course, "id" | "createdAt" | "updatedAt" | "isEnrolled" | "thumbnailUrl"> & { thumbnailUrl?: string };
export type CourseUpdatePayload = Partial<CourseCreatePayload>;

/**
 * Kiểu dữ liệu cho đăng ký khóa học
 */
export interface CourseEnrollment {
  id: number;
  userId: number;
  courseId: number;
  enrolledAt: string;
  status: string;
}

export interface EnrolledCourse extends Course {
  progress: number;
  status: string;
}

/**
 * Lấy danh sách khóa học có phân trang
 * @param page - Số trang
 * @param limit - Số lượng item mỗi trang
 * @returns Danh sách khóa học và thông tin phân trang
 */
export async function getCourses(page = 1, limit = 10) {
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
export async function getCourseById(id: number): Promise<Course> {
  const course = await get<Course>(`/courses/${id}`);
  // Đảm bảo tính tương thích giữa backend (is_enrolled) và frontend (isEnrolled)
  if ((course as any).is_enrolled !== undefined) {
    course.isEnrolled = (course as any).is_enrolled;
  }
  return course;
}

/**
 * Tạo khóa học mới
 * @param courseData Dữ liệu khóa học mới
 * @returns Khóa học vừa được tạo
 */
export async function createCourse(courseData: CourseCreatePayload): Promise<Course> {
  return post<Course>("/courses", courseData);
}

/**
 * Cập nhật khóa học
 * @param id ID của khóa học
 * @param courseData Dữ liệu cập nhật
 * @returns Khóa học sau khi cập nhật
 */
export async function updateCourse(id: number, courseData: CourseUpdatePayload): Promise<Course> {
  return put<Course>(`/courses/${id}`, courseData);
}

/**
 * Đăng ký khóa học
 * @param courseId - ID của khóa học
 * @returns Thông tin đăng ký khóa học
 */
export async function enrollCourse(courseId: number) {
  return post(`/courses/enroll`, { courseId });
}

/**
 * Hủy đăng ký khóa học
 * @param courseId - ID của khóa học
 * @returns Thông báo kết quả
 */
async function unregisterCourse(courseId: number) {
  return del(`/courses/enroll/${courseId}`)
    .then(() => ({ success: true, message: "Hủy đăng ký khóa học thành công" }))
    .catch(error => {
      console.error("Lỗi khi hủy đăng ký khóa học:", error);
      return { success: false, message: error.response?.data?.detail || "Hủy đăng ký khóa học thất bại" };
    });
}

/**
 * Kiểm tra trạng thái đăng ký khóa học
 * @param courseId - ID của khóa học
 * @returns Trạng thái đăng ký
 */
async function checkEnrollmentStatus(courseId: number) {
  return get<{ is_enrolled: boolean }>(`/user-courses/check-enrollment/${courseId}`);
}

/**
 * Lấy danh sách khóa học đã đăng ký
 * @returns Danh sách khóa học đã đăng ký
 */
export async function getEnrolledCourses(): Promise<EnrolledCourse[]> {
  return get<EnrolledCourse[]>("/courses/user/enrolled");
}

export async function getCourseTopics(courseId: number) {
  return get(`/courses/${courseId}/user-topics`);
}

export const coursesApi = {
  getCourses,
  getCourseById,
  createCourse,
  updateCourse,
  enrollCourse,
  unregisterCourse,
  checkEnrollmentStatus,
  getEnrolledCourses,
  getCourseTopics,
};

