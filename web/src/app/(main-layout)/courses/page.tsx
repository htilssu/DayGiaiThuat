"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { coursesApi, Course } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useAppDispatch, useAppSelector } from "@/lib/store";
import { addModal } from "@/lib/store/modalStore";
import { ModalWithCallbacks } from "@/lib/store/modalStore";
import { v4 as uuidv4 } from "uuid";
import { testApi } from "@/lib/api";

/**
 * Component hiển thị danh sách khóa học
 */
export default function CourseListPage() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const router = useRouter();
  const dispatch = useAppDispatch();
  const userState = useAppSelector((state) => state.user);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setIsLoading(true);
        const response = await coursesApi.getCourses(currentPage, 6);
        setCourses(response.items);
        setTotalPages(response.totalPages);
        setError(null);
      } catch (err) {
        console.error("Lỗi khi tải khóa học:", err);
        setError("Không thể tải danh sách khóa học. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCourses();
  }, [currentPage]);

  // Xử lý chuyển trang
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Chuyển đổi phút thành định dạng giờ:phút
  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours > 0 ? `${hours} giờ ` : ""}${mins > 0 ? `${mins} phút` : ""
      }`;
  };

  // Xử lý đăng ký khóa học
  const handleRegisterCourse = async (courseId: number) => {
    if (!userState.user) {
      // Nếu chưa đăng nhập, chuyển hướng đến trang đăng nhập với returnUrl
      const returnUrl = `/courses`;
      router.push(`/auth/login?returnUrl=${encodeURIComponent(returnUrl)}`);
      return;
    }

    // Hiển thị modal xác nhận đăng ký
    const course = courses.find(c => c.id === courseId);
    if (!course) return;

    dispatch(addModal({
      id: uuidv4(),
      title: "Xác nhận đăng ký khóa học",
      description: (
        <div>
          <p>Bạn có chắc chắn muốn đăng ký khóa học <strong>{course.title}</strong>?</p>
          {course.price && course.price > 0 ? (
            <p className="mt-2">Giá: <strong>{course.price.toLocaleString('vi-VN')}₫</strong></p>
          ) : (
            <p className="mt-2">Khóa học này <strong>miễn phí</strong>.</p>
          )}
        </div>
      ),
      onConfirm: () => confirmEnrollCourse(courseId, course),
      onCancel: () => { },
    }));
  };

  // Kiểm tra xem có bài kiểm tra đầu vào cho khóa học này không
  const checkForEntranceTest = async (courseId: number) => {
    try {
      // Giả sử khóa học có liên kết với topic có cùng ID
      const test = await testApi.getTestByTopic(courseId.toString());
      return test !== null;
    } catch (err) {
      console.error("Lỗi khi kiểm tra bài kiểm tra đầu vào:", err);
      return false;
    }
  };

  // Hiển thị modal bài kiểm tra đầu vào
  const showEntranceTestModal = (courseId: number) => {
    dispatch(addModal({
      id: uuidv4(),
      title: "Làm bài kiểm tra đầu vào",
      description: (
        <div>
          <p>Bạn đã đăng ký khóa học thành công!</p>
          <p className="mt-2">Để giúp chúng tôi đánh giá trình độ và cung cấp lộ trình học phù hợp, vui lòng làm bài kiểm tra đầu vào.</p>
        </div>
      ),
      onConfirm: () => handleStartEntranceTest(courseId),
      onCancel: () => router.push(`/topics/${courseId}`),
      confirmText: "Làm bài kiểm tra",
      cancelText: "Để sau",
    }));
  };

  // Xử lý bắt đầu làm bài kiểm tra đầu vào
  const handleStartEntranceTest = async (courseId: number) => {
    try {
      // Lấy thông tin bài kiểm tra
      const test = await testApi.getTestByTopic(courseId.toString());

      if (!test) {
        console.error("Không tìm thấy bài kiểm tra cho topic này");
        router.push(`/topics/${courseId}`);
        return;
      }

      // Tạo session kiểm tra mới
      if (userState.user) {
        try {
          // Kiểm tra xem đã có session nào đang hoạt động chưa
          const userSessions = await testApi.getMyTestSessions();
          const activeSession = userSessions.find(
            session =>
              session.test_id === parseInt(test.id) &&
              session.status === 'in_progress' &&
              !session.is_submitted
          );

          // Nếu đã có session đang hoạt động cho bài kiểm tra này, sử dụng session đó
          if (activeSession) {
            router.push(`/tests/topic-${courseId}`);
            return;
          }

          // Kiểm tra xem có session nào khác đang hoạt động không
          const otherActiveSessions = userSessions.filter(
            session =>
              session.status === 'in_progress' &&
              !session.is_submitted
          );

          if (otherActiveSessions.length > 0) {
            // Hiển thị thông báo và chuyển hướng đến session đang hoạt động
            const activeSessionTestId = otherActiveSessions[0].test_id;

            dispatch(addModal({
              id: uuidv4(),
              title: "Phiên làm bài đang hoạt động",
              description: "Bạn đang có một phiên làm bài kiểm tra khác đang hoạt động. Vui lòng hoàn thành hoặc hủy phiên đó trước khi bắt đầu phiên mới.",
              onConfirm: () => {
                // Chuyển đến phiên đang hoạt động
                router.push(`/tests/${activeSessionTestId}`);
              },
              onCancel: () => router.push(`/topics/${courseId}`),
              confirmText: "Đến phiên đang hoạt động",
              cancelText: "Quay lại",
            }));
            return;
          }

          // Nếu không có session nào đang hoạt động, tạo session mới
          const sessionData = {
            user_id: userState.user.id,
            test_id: parseInt(test.id)
          };
          await testApi.createTestSession(sessionData);

          // Chuyển hướng đến trang làm bài kiểm tra
          router.push(`/tests/topic-${courseId}`);
        } catch (error: any) {
          console.error("Lỗi khi tạo phiên kiểm tra:", error);

          // Xử lý lỗi khi đã có phiên đang hoạt động
          if (error.response?.status === 400 && error.response?.data?.detail?.includes("phiên làm bài kiểm tra khác đang hoạt động")) {
            dispatch(addModal({
              id: uuidv4(),
              title: "Phiên làm bài đang hoạt động",
              description: error.response.data.detail,
              onConfirm: () => {
                // Chuyển đến trang danh sách kiểm tra
                router.push(`/tests`);
              },
              onCancel: () => router.push(`/topics/${courseId}`),
              confirmText: "Xem danh sách kiểm tra",
              cancelText: "Quay lại",
            }));
            return;
          }

          // Hiển thị thông báo lỗi chung
          dispatch(addModal({
            id: uuidv4(),
            title: "Lỗi",
            description: "Không thể tạo phiên kiểm tra. Vui lòng thử lại sau.",
            onConfirm: () => router.push(`/topics/${courseId}`),
            onCancel: () => { },
          }));
        }
      } else {
        // Nếu không có thông tin người dùng, chuyển hướng đến trang đăng nhập
        router.push(`/auth/login?returnUrl=${encodeURIComponent(`/tests/topic-${courseId}`)}`);
      }
    } catch (error) {
      console.error("Lỗi khi tạo phiên kiểm tra:", error);
      // Hiển thị thông báo lỗi
      dispatch(addModal({
        id: uuidv4(),
        title: "Lỗi",
        description: "Không thể tạo phiên kiểm tra. Vui lòng thử lại sau.",
        onConfirm: () => router.push(`/topics/${courseId}`),
        onCancel: () => { },
      }));
    }
  };

  // Xác nhận đăng ký khóa học
  const confirmEnrollCourse = async (courseId: number, course: Course) => {
    try {
      const response = await coursesApi.registerCourse(courseId);

      if (response.success) {
        // Cập nhật danh sách khóa học để hiển thị trạng thái đăng ký mới
        setCourses(courses.map(c =>
          c.id === courseId ? { ...c, isEnrolled: true } : c
        ));

        // Kiểm tra xem có bài kiểm tra đầu vào cho khóa học này không
        const hasEntranceTest = await checkForEntranceTest(courseId);

        if (hasEntranceTest) {
          dispatch(addModal({
            id: uuidv4(),
            title: "Đăng ký thành công",
            description: "Bạn sẽ được chuyển đến bài kiểm tra đầu vào để đánh giá trình độ.",
            onConfirm: () => handleStartEntranceTest(courseId),
            confirmText: "Bắt đầu kiểm tra",
          }));
        } else {
          // Hiển thị thông báo đăng ký thành công
          dispatch(addModal({
            id: uuidv4(),
            title: "Đăng ký thành công",
            description: "Bạn đã đăng ký khóa học thành công!",
            onConfirm: () => {},
            onCancel: () => { },
            confirmText: "Đi đến khóa học",
          }));
        }
      } else {
        // Hiển thị thông báo lỗi
        dispatch(addModal({
          id: uuidv4(),
          title: "Đăng ký thất bại",
          description: response.message || "Có lỗi xảy ra khi đăng ký khóa học. Vui lòng thử lại sau.",
          onConfirm: () => { },
          onCancel: () => { },
        }));
      }
    } catch (err) {
      console.error("Lỗi khi đăng ký khóa học:", err);
      // Hiển thị thông báo lỗi
      dispatch(addModal({
        id: uuidv4(),
        title: "Đăng ký thất bại",
        description: "Có lỗi xảy ra khi đăng ký khóa học. Vui lòng thử lại sau.",
        onConfirm: () => { },
        onCancel: () => { },
      }));
    }
  };

  // Xử lý hủy đăng ký khóa học
  const handleUnregisterCourse = async (courseId: number) => {
    const course = courses.find(c => c.id === courseId);
    if (!course) return;

    // Hiển thị modal xác nhận hủy đăng ký
    dispatch(addModal({
      id: uuidv4(),
      title: "Xác nhận hủy đăng ký",
      description: (
        <div>
          <p>Bạn có chắc chắn muốn hủy đăng ký khóa học <strong>{course.title}</strong>?</p>
          <p className="mt-2 text-accent">Lưu ý: Bạn sẽ mất tiến độ học tập trong khóa học này.</p>
        </div>
      ),
      onConfirm: () => confirmUnregisterCourse(courseId),
      onCancel: () => { },
      confirmText: "Hủy đăng ký",
      cancelText: "Giữ lại",
    }));
  };

  // Xác nhận hủy đăng ký khóa học
  const confirmUnregisterCourse = async (courseId: number) => {
    try {
      const response = await coursesApi.unregisterCourse(courseId);

      if (response.success) {
        // Cập nhật danh sách khóa học để hiển thị trạng thái đăng ký mới
        setCourses(courses.map(c =>
          c.id === courseId ? { ...c, isEnrolled: false } : c
        ));

        // Hiển thị thông báo hủy đăng ký thành công
        dispatch(addModal({
          id: uuidv4(),
          title: "Hủy đăng ký thành công",
          description: "Bạn đã hủy đăng ký khóa học thành công!",
          onConfirm: () => { },
          onCancel: () => { },
        }));
      } else {
        // Hiển thị thông báo lỗi
        dispatch(addModal({
          id: uuidv4(),
          title: "Hủy đăng ký thất bại",
          description: response.message || "Có lỗi xảy ra khi hủy đăng ký khóa học. Vui lòng thử lại sau.",
          onConfirm: () => { },
          onCancel: () => { },
        }));
      }
    } catch (err) {
      console.error("Lỗi khi hủy đăng ký khóa học:", err);
      // Hiển thị thông báo lỗi
      dispatch(addModal({
        id: uuidv4(),
        title: "Hủy đăng ký thất bại",
        description: "Có lỗi xảy ra khi hủy đăng ký khóa học. Vui lòng thử lại sau.",
        onConfirm: () => { },
        onCancel: () => { },
      }));
    }
  };

  return (
    <div className="py-10 px-4 max-w-7xl mx-auto">
      {/* Banner */}
      <div className="relative w-full h-80 mb-12 overflow-hidden rounded-2xl">
        <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary opacity-90 z-10"></div>
        <div className="absolute inset-0 bg-grid-white z-0"></div>
        <div className="absolute inset-0 flex flex-col justify-center items-center text-white z-20 p-6 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 animate-fade-in">
            Khóa Học Thuật Toán
          </h1>
          <p
            className="text-lg md:text-xl max-w-3xl animate-fade-in"
            style={{ animationDelay: "0.2s" }}>
            Nâng cao kỹ năng lập trình và tư duy giải quyết vấn đề với các khóa
            học chất lượng cao
          </p>
        </div>
      </div>

      {/* Filter & Search - có thể phát triển thêm */}
      <div className="mb-10 flex flex-col md:flex-row justify-between items-center gap-4">
        <h2 className="text-3xl font-bold">Tất Cả Khóa Học</h2>
        <div className="relative w-full md:w-64">
          <input
            type="text"
            placeholder="Tìm kiếm khóa học..."
            className="w-full py-2 px-4 rounded-lg border border-foreground/20 bg-background"
          />
        </div>
      </div>

      {/* Danh sách khóa học */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="bg-foreground/5 rounded-xl p-4 h-96 animate-pulse"></div>
          ))}
        </div>
      ) : error ? (
        <div className="text-center py-10">
          <p className="text-lg text-accent">{error}</p>
          <button
            onClick={() => setCurrentPage(1)}
            className="mt-4 px-6 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition">
            Thử lại
          </button>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {courses.map((course) => (
              <div key={course.id} className="group bg-background rounded-xl overflow-hidden border border-foreground/10 hover:border-primary transition-all duration-300 h-full flex flex-col">
                {/* Thumbnail */}
                <Link href={`/courses/${course.id}`}>
                  <div className="relative w-full h-48 overflow-hidden">
                    {course.thumbnailUrl ? (
                      <Image
                        src={course.thumbnailUrl}
                        alt={course.title}
                        fill
                        className="object-cover transform group-hover:scale-105 transition-transform duration-500"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
                        <span className="text-4xl text-primary">Α</span>
                      </div>
                    )}
                    <div className="absolute top-2 right-2 bg-background/80 backdrop-blur-sm text-foreground text-sm font-medium py-1 px-3 rounded-full">
                      {course.level}
                    </div>
                    {course.price > 0 ? (
                      <div className="absolute bottom-2 left-2 bg-accent/90 text-white text-sm font-medium py-1 px-3 rounded-full">
                        {course.price.toLocaleString("vi-VN")} ₫
                      </div>
                    ) : (
                      <div className="absolute bottom-2 left-2 bg-primary/90 text-white text-sm font-medium py-1 px-3 rounded-full">
                        Miễn phí
                      </div>
                    )}
                  </div>
                </Link>

                {/* Nội dung */}
                <div className="p-5 flex flex-col flex-grow">
                  <Link href={`/courses/${course.id}`}>
                    <h3 className="font-bold text-xl mb-2 line-clamp-2 group-hover:text-primary transition-colors">
                      {course.title}
                    </h3>
                  </Link>
                  <p className="text-foreground/70 text-sm line-clamp-3 mb-4 flex-grow">
                    {course.description || "Không có mô tả cho khóa học này."}
                  </p>
                  <div className="mt-auto pt-3 border-t border-foreground/10 flex items-center justify-between">
                    <div className="flex items-center text-foreground/70 text-sm">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 mr-1"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      {formatDuration(course.duration)}
                    </div>
                    {course.isEnrolled ? (
                      <div className="flex gap-2">
                        <Link href={`/topics/${course.id}`} className="flex items-center text-primary font-medium">
                          Tiếp tục học
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M9 5l7 7-7 7"
                            />
                          </svg>
                        </Link>
                        <button
                          onClick={() => handleUnregisterCourse(course.id)}
                          className="flex items-center text-accent font-medium ml-4">
                          Hủy
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleRegisterCourse(course.id)}
                        className="flex items-center text-primary font-medium">
                        Đăng ký ngay
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M9 5l7 7-7 7"
                          />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Phân trang */}
          {totalPages > 1 && (
            <div className="flex justify-center mt-12">
              <div className="flex space-x-2">
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 rounded-md border border-foreground/20 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-foreground/5">
                  Trước
                </button>
                {[...Array(totalPages)].map((_, i) => (
                  <button
                    key={i}
                    onClick={() => handlePageChange(i + 1)}
                    className={`px-4 py-2 rounded-md border ${currentPage === i + 1
                      ? "bg-primary text-white border-primary"
                      : "border-foreground/20 hover:bg-foreground/5"
                      }`}>
                    {i + 1}
                  </button>
                ))}
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 rounded-md border border-foreground/20 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-foreground/5">
                  Sau
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
