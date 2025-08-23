/**
 * API client cho các thao tác với khóa học
 * @module api/courses
 */

import { get, post, del } from "./client";
import { Test, TestSession } from "./test";
import { Topic } from "./topics";

/**
 * Kiểu dữ liệu cho lesson
 */


/**
 * Kiểu dữ liệu cho topic với lessons
 */


/**
 * Kiểu dữ liệu cho item trong danh sách khóa học (không bao gồm topics)
 */
export interface CourseListItem {
  id: number;
  title: string;
  description: string | null;
  thumbnailUrl: string | null;
  level: string;
  duration: number;
  price: number;
  tags: string;
  createdAt: string;
  updatedAt: string;
  isEnrolled?: boolean;
}

/**
 * Kiểu dữ liệu cho khóa học chi tiết
 */
export interface UserCourseDetail {
  id: number;
  title: string;
  description: string | null;
  thumbnailUrl: string | null;
  level: string;
  duration: number;
  price: number;
  status: string | null;
  isPublished: boolean;
  tags: string;
  requirements: string | null;
  whatYouWillLearn: string | null;
  createdAt: string;
  updatedAt: string;
  testGenerationStatus?: string;
  isEnrolled?: boolean;
  topics: Topic[];
}

/**
 * Kiểu dữ liệu cho đăng ký khóa học
 */
export interface CourseEnrollment {
  id: number;
  userId: number;
  courseId: number;
  createdAt: string;
  updatedAt: string;
}

/**
 * Kiểu dữ liệu cho response đăng ký khóa học
 */
export interface CourseEnrollmentResponse {
  enrollment: CourseEnrollment;
  hasEntryTest: boolean;
  entryTestId: number | null;
}

export interface EnrolledCourse extends UserCourseDetail {
  progress: number;
  status: string;
  currentTopicId?: number | null;
  currentLessonId?: number | null;
}

/**
 * Lấy danh sách khóa học có phân trang
 * @param page - Số trang
 * @param limit - Số lượng item mỗi trang
 * @returns Danh sách khóa học cơ bản và thông tin phân trang
 */
export async function getCourses(page = 1, limit = 10) {
  return get<{
    items: CourseListItem[];
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  }>(`/courses`, { params: { page, limit } });
}

/**
 * Lấy thông tin chi tiết của một khóa học bao gồm topics và lessons
 * @param id - ID của khóa học
 * @returns Thông tin chi tiết khóa học với topics và lessons
 */
export async function getCourseById(id: number): Promise<UserCourseDetail> {
  const course = await get<UserCourseDetail>(`/courses/${id}`);
  // Đảm bảo tính tương thích giữa backend (is_enrolled) và frontend (isEnrolled)
  if ((course as any).isEnrolled !== undefined) {
    course.isEnrolled = (course as any).isEnrolled;
  }
  return course;
}

/**
 * Đăng ký khóa học
 * @param courseId - ID của khóa học
 * @returns Thông tin đăng ký khóa học
 */
export async function enrollCourse(
  courseId: number
): Promise<CourseEnrollmentResponse> {
  return post<CourseEnrollmentResponse>(`/courses/enroll`, {
    courseId: courseId,
  });
}

/**
 * Hủy đăng ký khóa học
 * @param courseId - ID của khóa học
 * @returns Thông báo kết quả
 */
async function unregisterCourse(courseId: number) {
  return del(`/courses/enroll/${courseId}`)
    .then(() => ({ success: true, message: "Hủy đăng ký khóa học thành công" }))
    .catch((error) => {
      console.error("Lỗi khi hủy đăng ký khóa học:", error);
      return {
        success: false,
        message:
          error.response?.data?.detail || "Hủy đăng ký khóa học thất bại",
      };
    });
}

/**
 * Lấy danh sách khóa học đã đăng ký
 * @returns Danh sách khóa học đã đăng ký
 */
export async function getEnrolledCourses(): Promise<EnrolledCourse[]> {
  return get<EnrolledCourse[]>("/courses/enrolled");
}

export async function getCourseTopics(courseId: number) {
  return get<Topic[]>(`/courses/${courseId}/topics`);
}

/**
 * Lấy test đầu vào của khóa học
 * @param courseId - ID của khóa học
 * @returns Test đầu vào
 */
export async function getCourseEntryTest(courseId: number): Promise<Test> {
  return get<Test>(`/courses/${courseId}/entry-test`);
}

/**
 * Bắt đầu làm bài test đầu vào của khóa học
 * @param courseId - ID của khóa học
 * @returns Test session đã được tạo
 */
export async function startCourseEntryTest(
  courseId: number
): Promise<TestSession> {
  return post<TestSession>(`/courses/${courseId}/entry-test/start`, {});
}

/**
 * Đánh dấu khóa học hoàn thành dựa trên test đã vượt qua
 * @param courseId - ID của khóa học
 * @param testSessionId - ID của phiên test đã vượt qua
 * @returns Kết quả đánh dấu hoàn thành
 */
export async function markCourseCompleted(
  courseId: number,
  testSessionId: string
): Promise<{
  message: string;
  courseId: number;
  completedAt: string;
  testSessionId: string;
  score: number;
}> {
  return post(`/courses/${courseId}/complete`, testSessionId);
}

/**
 * Kiểm tra trạng thái đăng ký khóa học
 * @param courseId - ID của khóa học
 * @returns Trạng thái đăng ký khóa học
 */
export async function checkEnrollmentStatus(courseId: number): Promise<{ isEnrolled: boolean }> {
  return get<{ isEnrolled: boolean }>(`/courses/${courseId}/check-enrollment`);
}


export const coursesApi = {
  getCourses,
  getCourseById,
  enrollCourse,
  unregisterCourse,
  checkEnrollmentStatus,
  getEnrolledCourses,
  getCourseTopics,
  getCourseEntryTest,
  startCourseEntryTest,
  markCourseCompleted,
};
