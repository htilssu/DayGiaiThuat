"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { useParams, useRouter } from "next/navigation";
import { coursesApi } from "@/lib/api";
import { Course } from "@/lib/api/courses";
import { dsaCourseContent } from "@/data/courseContent";
import Link from "next/link";
import { useAppDispatch, useAppSelector } from "@/lib/store";
import { addModal } from "@/lib/store/modalStore";
import { reloadUser } from "@/lib/store/userStore";
import { v4 as uuidv4 } from "uuid";
import { testApi } from "@/lib/api";
import { ModalWithCallbacks } from "@/lib/store/modalStore";


/**
 * Component hiển thị chi tiết khóa học
 */
export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const courseId = Number(params.id);
  const userState = useAppSelector((state) => state.user);


  const [course, setCourse] = useState<Course | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "overview" | "content" | "reviews"
  >("overview");

  const [isUnregistering, setIsUnregistering] = useState<boolean>(false);
  const [isEnrolled, setIsEnrolled] = useState<boolean>(false);
  const [isRegistering, setIsRegistering] = useState<boolean>(false);

  useEffect(() => {
    const fetchCourseDetails = async () => {
      try {
        setIsLoading(true);
        const data = await coursesApi.getCourseById(courseId);
        setCourse(data);

        // Sử dụng trạng thái đăng ký từ phản hồi API
        // Backend sẽ tự động kiểm tra trạng thái đăng ký nếu người dùng đã đăng nhập
        setIsEnrolled(data.isEnrolled || false);
      } catch (err) {
        console.error("Lỗi khi tải thông tin khóa học:", err);
        setError("Không thể tải thông tin khóa học. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };

    if (courseId) {
      fetchCourseDetails();
    }
  }, [courseId]);

  // Chuyển đổi phút thành định dạng giờ:phút
  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours > 0 ? `${hours} giờ ` : ""}${mins > 0 ? `${mins} phút` : ""
      }`;
  };

  // Tạo mảng từ chuỗi phân cách bằng dấu phẩy
  const getTagsArray = (tags: string) => {
    return tags.split(",").filter((tag) => tag.trim() !== "");
  };

  // Parse JSON từ chuỗi
  const parseJsonString = (jsonString: string | null) => {
    if (!jsonString) return [];
    try {
      return JSON.parse(jsonString);
    } catch (error) {
      console.error("Lỗi khi parse JSON:", error);
      return [];
    }
  };

  // Xử lý đăng ký khóa học
  const handleRegisterCourse = () => {
    if (!userState.user) {
      // Nếu chưa đăng nhập, chuyển hướng đến trang đăng nhập với returnUrl
      const returnUrl = `/courses/${courseId}`;
      router.push(`/auth/login?returnUrl=${encodeURIComponent(returnUrl)}`);
      return;
    }

    // Hiển thị modal xác nhận đăng ký
    dispatch(addModal({
      id: uuidv4(),
      title: "Xác nhận đăng ký khóa học",
      description: (
        <div>
          <p>Bạn có chắc chắn muốn đăng ký khóa học <strong>{course?.title}</strong>?</p>
          {course?.price && course.price > 0 ? (
            <p className="mt-2">Giá: <strong>{course.price.toLocaleString('vi-VN')}₫</strong></p>
          ) : (
            <p className="mt-2">Khóa học này <strong>miễn phí</strong>.</p>
          )}
        </div>
      ),
      onConfirm: () => confirmEnrollCourse(),
      onCancel: () => { },
    }));
  };

  // Xác nhận đăng ký khóa học
  const confirmEnrollCourse = async () => {
    try {
      setIsRegistering(true);
      const response = await coursesApi.registerCourse(courseId);

      if (response.success) {
        // Cập nhật trạng thái đăng ký
        setIsEnrolled(true);

        // Đặt lại isInitial thành true để load lại thông tin người dùng
        dispatch(reloadUser());

        // Kiểm tra xem có bài kiểm tra đầu vào cho khóa học này không
        const hasEntranceTest = await checkForEntranceTest();

        if (hasEntranceTest) {
          dispatch(addModal({
            id: uuidv4(),
            title: "Đăng ký thành công",
            description: "Bạn sẽ được chuyển đến bài kiểm tra đầu vào để đánh giá trình độ.",
            onConfirm: () => handleStartEntranceTest(),
            onCancel: () => { },
            confirmText: "Bắt đầu kiểm tra",
          }));
        } else {
          // Hiển thị thông báo đăng ký thành công
          dispatch(addModal({
            id: uuidv4(),
            title: "Đăng ký thành công",
            description: "Bạn đã đăng ký khóa học thành công!",
            onConfirm: () => { },
            onCancel: () => { },
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
    } finally {
      setIsRegistering(false);
    }
  };

  // Kiểm tra xem có bài kiểm tra đầu vào cho khóa học này không
  const checkForEntranceTest = async () => {
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
  const showEntranceTestModal = () => {
    dispatch(addModal({
      id: uuidv4(),
      title: "Làm bài kiểm tra đầu vào",
      description: (
        <div>
          <p>Bạn đã đăng ký khóa học thành công!</p>
          <p className="mt-2">Để giúp chúng tôi đánh giá trình độ và cung cấp lộ trình học phù hợp, vui lòng làm bài kiểm tra đầu vào.</p>
        </div>
      ),
      onConfirm: () => handleStartEntranceTest(),
      onCancel: () => router.push(`/topics/${courseId}`),
      confirmText: "Làm bài kiểm tra",
      cancelText: "Để sau",
    }));
  };

  // Xử lý bắt đầu làm bài kiểm tra đầu vào
  const handleStartEntranceTest = async () => {
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

  // Xử lý hủy đăng ký khóa học
  const handleUnregisterCourse = async () => {
    try {
      setIsUnregistering(true);
      const response = await coursesApi.unregisterCourse(courseId);

      if (response.success) {
        // Cập nhật trạng thái đăng ký
        setIsEnrolled(false);

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
    } finally {
      setIsUnregistering(false);
    }
  };



  if (isLoading) {
    return (
      <div className="py-16 px-4 max-w-6xl mx-auto">
        <div className="w-full h-64 bg-foreground/5 rounded-xl animate-pulse mb-8"></div>
        <div className="w-3/4 h-10 bg-foreground/5 rounded animate-pulse mb-6"></div>
        <div className="w-full h-40 bg-foreground/5 rounded animate-pulse"></div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="py-16 px-4 max-w-6xl mx-auto text-center">
        <div className="bg-foreground/5 rounded-xl p-10">
          <h1 className="text-2xl font-bold mb-4 text-accent">
            {error || "Không tìm thấy khóa học"}
          </h1>
          <p className="mb-6 text-foreground/70">
            Khóa học bạn đang tìm kiếm không tồn tại hoặc đã bị xóa.
          </p>
          <button
            onClick={() => router.push("/courses")}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
            Quay lại danh sách khóa học
          </button>
        </div>
      </div>
    );
  }

  // Phân tích dữ liệu từ JSON
  const requirements = parseJsonString(course.requirements);
  const whatYouWillLearn = parseJsonString(course.whatYouWillLearn);

  return (
    <div className="py-10 px-4">
      {/* Hero section */}
      <div className="relative w-full bg-foreground/5 overflow-hidden">
        <div className="max-w-6xl mx-auto py-16 px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <div className="flex items-center mb-4">
                <span className="bg-primary/10 text-primary text-sm font-medium py-1 px-3 rounded-full">
                  {course.level}
                </span>
                {course.tags && (
                  <span className="ml-2 text-foreground/60 text-sm">
                    {getTagsArray(course.tags).join(" • ")}
                  </span>
                )}
              </div>

              <h1 className="text-3xl md:text-4xl font-bold mb-4">
                {course.title}
              </h1>

              <p className="text-foreground/80 text-lg mb-6">
                {course.description}
              </p>

              <div className="flex items-center gap-4 mb-8">
                <div className="flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-primary mr-2"
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
                  <span>{formatDuration(course.duration)}</span>
                </div>
                <div className="flex items-center">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5 text-primary mr-2"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <span>
                    Cập nhật{" "}
                    {new Date(course.updatedAt).toLocaleDateString("vi-VN")}
                  </span>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                {isEnrolled ? (
                  <>
                    <Link
                      href={`/topics/${courseId}`}
                      className="px-8 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition font-medium text-center">
                      Tiếp tục học
                    </Link>
                    <button
                      onClick={handleUnregisterCourse}
                      disabled={isUnregistering}
                      className="px-8 py-3 bg-destructive/10 text-destructive border border-destructive/20 rounded-lg hover:bg-destructive/20 transition font-medium disabled:opacity-70 disabled:cursor-not-allowed">
                      {isUnregistering ? "Đang xử lý..." : "Hủy đăng ký"}
                    </button>
                  </>
                ) : (
                  <button
                    onClick={handleRegisterCourse}
                    disabled={isRegistering}
                    className="px-8 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition font-medium disabled:opacity-70 disabled:cursor-not-allowed">
                    {isRegistering
                      ? "Đang xử lý..."
                      : course.price > 0
                        ? `Đăng ký - ${course.price.toLocaleString("vi-VN")}₫`
                        : "Đăng ký miễn phí"}
                  </button>
                )}
                <button
                  onClick={() => setActiveTab("content")}
                  className="px-8 py-3 border border-foreground/20 rounded-lg hover:bg-foreground/5 transition font-medium">
                  Xem trước
                </button>
              </div>
            </div>

            <div className="relative h-64 md:h-80 lg:h-auto rounded-xl overflow-hidden">
              {course.thumbnailUrl ? (
                <Image
                  src={course.thumbnailUrl}
                  alt={course.title}
                  fill
                  className="object-cover"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center">
                  <span className="text-6xl text-primary">Α</span>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="absolute inset-0 bg-grid-white opacity-30"></div>
      </div>

      {/* Content section */}
      <div className="max-w-6xl mx-auto mt-10">
        {/* Tabs */}
        <div className="border-b border-foreground/10 mb-8">
          <div className="flex flex-wrap -mb-px">
            <button
              onClick={() => setActiveTab("overview")}
              className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${activeTab === "overview"
                ? "border-primary text-primary"
                : "border-transparent hover:text-primary/80 hover:border-foreground/20"
                }`}>
              Tổng quan
            </button>
            <button
              onClick={() => setActiveTab("content")}
              className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${activeTab === "content"
                ? "border-primary text-primary"
                : "border-transparent hover:text-primary/80 hover:border-foreground/20"
                }`}>
              Nội dung khóa học
            </button>
            <button
              onClick={() => setActiveTab("reviews")}
              className={`mr-8 py-4 px-1 border-b-2 font-medium text-sm ${activeTab === "reviews"
                ? "border-primary text-primary"
                : "border-transparent hover:text-primary/80 hover:border-foreground/20"
                }`}>
              Đánh giá
            </button>
          </div>
        </div>

        {/* Tab content */}
        <div className="px-1">
          {activeTab === "overview" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="mb-10">
                  <h2 className="text-2xl font-bold mb-6">Mô tả khóa học</h2>
                  <div className="prose max-w-none text-foreground/80">
                    <p>
                      {course.description ||
                        "Không có mô tả chi tiết cho khóa học này."}
                    </p>
                  </div>
                </div>

                {whatYouWillLearn.length > 0 && (
                  <div className="mb-10">
                    <h2 className="text-2xl font-bold mb-6">
                      Bạn sẽ học được gì
                    </h2>
                    <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {whatYouWillLearn.map((item: string, index: number) => (
                        <li key={index} className="flex items-start">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5 text-primary mr-2 flex-shrink-0 mt-0.5"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              <div>
                {requirements.length > 0 && (
                  <div className="p-6 bg-foreground/5 rounded-xl mb-8">
                    <h3 className="text-lg font-bold mb-4">
                      Yêu cầu trước khóa học
                    </h3>
                    <ul className="space-y-2">
                      {requirements.map((item: string, index: number) => (
                        <li key={index} className="flex items-start">
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-5 w-5 text-primary mr-2 flex-shrink-0"
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
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="p-6 bg-foreground/5 rounded-xl">
                  <h3 className="text-lg font-bold mb-4">Thông tin khóa học</h3>
                  <ul className="space-y-4">
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Cấp độ</span>
                      <span className="font-medium">{course.level}</span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Thời lượng</span>
                      <span className="font-medium">
                        {formatDuration(course.duration)}
                      </span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Giá</span>
                      <span className="font-medium">
                        {course.price > 0
                          ? `${course.price.toLocaleString("vi-VN")}₫`
                          : "Miễn phí"}
                      </span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Ngày tạo</span>
                      <span className="font-medium">
                        {new Date(course.createdAt).toLocaleDateString("vi-VN")}
                      </span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Cập nhật</span>
                      <span className="font-medium">
                        {new Date(course.updatedAt).toLocaleDateString("vi-VN")}
                      </span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === "content" && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Nội dung khóa học</h2>
              <div className="space-y-4">
                {dsaCourseContent.map((chapter) => (
                  <details
                    key={chapter.id}
                    className="group bg-foreground/5 rounded-xl overflow-hidden"
                    open={chapter.id === 1}>
                    <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-foreground/10">
                      <div>
                        <h3 className="font-medium">
                          Chương {chapter.id}: {chapter.title}
                        </h3>
                        <p className="text-sm text-foreground/70 mt-1">
                          {chapter.description}
                        </p>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-sm text-foreground/70">
                          {chapter.lessons.length} bài học
                        </div>
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          className="h-5 w-5 transform transition-transform group-open:rotate-180"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                          />
                        </svg>
                      </div>
                    </summary>
                    <div className="border-t border-foreground/10">
                      {chapter.lessons.map((lesson) => (
                        <div
                          key={lesson.id}
                          className="flex items-center gap-4 p-4 hover:bg-foreground/5">
                          <div
                            className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${lesson.type === "video"
                              ? "bg-blue-500/10 text-blue-500"
                              : lesson.type === "quiz"
                                ? "bg-purple-500/10 text-purple-500"
                                : "bg-green-500/10 text-green-500"
                              }`}>
                            {lesson.type === "video" ? (
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor">
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                                />
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                                />
                              </svg>
                            ) : lesson.type === "quiz" ? (
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor">
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                                />
                              </svg>
                            ) : (
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className="h-5 w-5"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor">
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                                />
                              </svg>
                            )}
                          </div>
                          <div className="flex-grow">
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium">{lesson.title}</h4>
                              {lesson.isPreview && (
                                <span className="px-2 py-0.5 text-xs bg-primary/10 text-primary rounded-full">
                                  Xem trước
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-foreground/70 mt-1">
                              {lesson.description}
                            </p>
                          </div>
                          <div className="flex items-center gap-3 flex-shrink-0">
                            <span className="text-sm text-foreground/70">
                              {lesson.duration} phút
                            </span>
                            {lesson.isPreview ? (
                              <Link
                                href={`/lessons/${lesson.id}`}
                                className="px-3 py-1 text-sm border border-primary text-primary rounded hover:bg-primary/10 transition">
                                Xem ngay
                              </Link>
                            ) : (
                              <button
                                disabled
                                className="px-3 py-1 text-sm border border-foreground/20 text-foreground/40 rounded cursor-not-allowed">
                                Khóa
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          )}

          {activeTab === "reviews" && (
            <div>
              <h2 className="text-2xl font-bold mb-6">Đánh giá từ học viên</h2>
              <div className="p-4 bg-foreground/5 text-center rounded-xl">
                <p className="text-lg">Chưa có đánh giá cho khóa học này</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
