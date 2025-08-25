"use client";

import { useState, useEffect, useMemo } from "react";
import Image from "next/image";
import { useParams, useRouter } from "next/navigation";
import { coursesApi, topicsApi, lessonsApi } from "@/lib/api";
import { UserCourseDetail } from "@/lib/api/courses";
import { testApi } from "@/lib/api/test";
import Link from "next/link";
import { useAppDispatch, useAppSelector } from "@/lib/store";
import { addModal } from "@/lib/store/modalStore";
import { reloadUser } from "@/lib/store/userStore";
import { v4 as uuidv4 } from "uuid";
import { useQuery, useQueryClient } from "@tanstack/react-query";

export default function CourseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const courseId = Number(params.id);
  const userState = useAppSelector((state) => state.user);
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState<"overview" | "content" | "reviews">("overview");
  const [isRegistering, setIsRegistering] = useState<boolean>(false);

  const { data: courseData, isLoading, error } = useQuery({
    queryKey: ["course", courseId],
    queryFn: () => coursesApi.getCourseById(courseId),
    enabled: !!courseId,
  });

  const { data: topicData, isLoading: topicIsLoading } = useQuery({
    queryKey: ["courseTopics", courseId],
    queryFn: () => coursesApi.getCourseTopics(courseId),
    enabled: !!courseId && !!courseData,
  });

  // Calculate if all lessons are completed
  const allLessonsCompleted = useMemo(() => {
    if (!courseData?.isEnrolled || !topicData?.length) return false;

    const totalLessons = topicData.reduce((total, topic) =>
      total + (topic.lessons?.length || 0), 0);
    const completedLessons = topicData.reduce((total, topic) =>
      total + (topic.lessons?.filter(lesson => lesson.isCompleted).length || 0), 0);

    return totalLessons > 0 && completedLessons === totalLessons;
  }, [courseData, topicData]);

  useEffect(() => {
    if (courseData) {
      topicData?.sort((a, b) => a.order - b.order);
    }
  }, [courseData]);


  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours > 0 ? `${hours} giờ ` : ""}${mins > 0 ? `${mins} phút` : ""}`;
  };

  const getTagsArray = (tags: string) => {
    return tags.split(",").filter((tag) => tag.trim() !== "");
  };

  const parseJsonString = (jsonString: string | null) => {
    if (!jsonString) return [];
    try {
      return JSON.parse(jsonString);
    } catch (error) {
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
          <p>Bạn có chắc chắn muốn đăng ký khóa học <strong>{courseData?.title}</strong>?</p>
          {courseData?.price && courseData.price > 0 ? (
            <p className="mt-2">Giá: <strong>{courseData.price.toLocaleString('vi-VN')}₫</strong></p>
          ) : (
            <p className="mt-2">Khóa học này <strong>miễn phí</strong>.</p>
          )}
        </div>
      ),
      onConfirm: () => confirmEnrollCourse(),
      onCancel: () => { },
    }));
  };

  const confirmEnrollCourse = async () => {
    try {
      setIsRegistering(true);
      const response = await coursesApi.enrollCourse(courseId);

      queryClient.invalidateQueries({ queryKey: ["course", courseId] });

      dispatch(reloadUser());

      if (response.hasEntryTest && response.entryTestId) {
        dispatch(addModal({
          id: uuidv4(),
          title: "Đăng ký thành công",
          description: "Bạn sẽ được chuyển đến bài kiểm tra đầu vào để đánh giá trình độ.",
          onConfirm: () => handleStartEntranceTest(),
          onCancel: () => { },
          confirmText: "Bắt đầu kiểm tra",
        }));
      } else {
        dispatch(addModal({
          id: uuidv4(),
          title: "Đăng ký thành công",
          description: "Bạn đã đăng ký khóa học thành công!",
          onConfirm: () => { },
          onCancel: () => { },
        }));
      }
    } catch (err) {
      console.error("Lỗi khi đăng ký khóa học:", err);
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

  const handleStartEntranceTest = async () => {
    try {
      if (!userState.user) {
        router.push(`/auth/login?returnUrl=${encodeURIComponent(`/courses/${courseId}`)}`);
        return;
      }

      router.push(`/tests/entry/${courseId}`);
    } catch (error: any) {
      console.error("Lỗi khi chuyển hướng:", error);
    }
  };

  // Xử lý bắt đầu làm bài kiểm tra hoàn thành khóa học
  const handleStartCourseTest = async () => {
    try {
      if (!userState.user) {
        router.push(`/auth/login?returnUrl=${encodeURIComponent(`/courses/${courseId}`)}`);
        return;
      }

      // Lấy danh sách tests của khóa học
      const tests = await testApi.getTestsByCourse(courseId);

      if (!tests || tests.length === 0) {
        dispatch(addModal({
          id: uuidv4(),
          title: "Không có bài kiểm tra",
          description: "Khóa học này chưa có bài kiểm tra nào. Vui lòng liên hệ với giảng viên.",
          onConfirm: () => { },
          onCancel: () => { },
        }));
        return;
      }

      // Chọn một test ngẫu nhiên
      const randomTest = tests[Math.floor(Math.random() * tests.length)];

      // Tạo test session
      const testSession = await testApi.createTestSession({ testId: randomTest.id });

      // Chuyển hướng đến trang làm bài test
      router.push(`/tests/${testSession.id}`);
    } catch (error: any) {
      console.error("Lỗi khi bắt đầu bài kiểm tra:", error);
      dispatch(addModal({
        id: uuidv4(),
        title: "Lỗi",
        description: "Có lỗi xảy ra khi bắt đầu bài kiểm tra. Vui lòng thử lại sau.",
        onConfirm: () => { },
        onCancel: () => { },
      }));
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

  if (error || !courseData) {
    return (
      <div className="py-16 px-4 max-w-6xl mx-auto text-center">
        <div className="bg-foreground/5 rounded-xl p-10">
          <h1 className="text-2xl font-bold mb-4 text-accent">
            {error?.message || "Không tìm thấy khóa học"}
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
  const requirements = parseJsonString(courseData.requirements);
  const whatYouWillLearn = parseJsonString(courseData.whatYouWillLearn);

  return (
    <div className="py-10 px-4">
      {/* Hero section */}
      <div className="relative w-full bg-foreground/5 overflow-hidden">
        <div className="max-w-6xl mx-auto py-16 px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <div className="flex items-center mb-4">
                <span className="bg-primary/10 text-primary text-sm font-medium py-1 px-3 rounded-full">
                  {courseData.level}
                </span>
                {courseData.tags && (
                  <span className="ml-2 text-foreground/60 text-sm">
                    {getTagsArray(courseData.tags).join(" • ")}
                  </span>
                )}
              </div>

              <h1 className="text-3xl md:text-4xl font-bold mb-4">
                {courseData.title}
              </h1>

              <p className="text-foreground/80 text-lg mb-6">
                {courseData.description}
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
                  <span>{formatDuration(courseData.duration)}</span>
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
                    {new Date(courseData.updatedAt).toLocaleDateString("vi-VN")}
                  </span>
                </div>
                {courseData?.isEnrolled && topicData && topicData.length > 0 && (
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
                        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                      />
                    </svg>
                    <span>
                      {(() => {
                        const totalLessons = topicData.reduce((total, topic) => total + (topic.lessons?.length || 0), 0);
                        const completedLessons = topicData.reduce((total, topic) =>
                          total + (topic.lessons?.filter(lesson => lesson.isCompleted).length || 0), 0);
                        return `${completedLessons}/${totalLessons} bài học`;
                      })()}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                {courseData?.isEnrolled ? (
                  <>
                    {allLessonsCompleted ? (
                      <button
                        onClick={handleStartCourseTest}
                        className="px-8 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition font-medium text-center">
                        Làm bài kiểm tra
                      </button>
                    ) : (
                      <Link
                        href={`/topics/${courseId}`}
                        className="px-8 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition font-medium text-center">
                        Tiếp tục học
                      </Link>
                    )}
                  </>
                ) : (
                  <button
                    onClick={handleRegisterCourse}
                    disabled={isRegistering}
                    className="px-8 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition font-medium disabled:opacity-70 disabled:cursor-not-allowed">
                    {isRegistering
                      ? "Đang xử lý..."
                      : courseData.price > 0
                        ? `Đăng ký - ${courseData.price.toLocaleString("vi-VN")}₫`
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
              {courseData.thumbnailUrl ? (
                <Image
                  src={courseData.thumbnailUrl}
                  alt={courseData.title}
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
                      {courseData.description ||
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
                      <span className="font-medium">{courseData.level}</span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Thời lượng</span>
                      <span className="font-medium">
                        {formatDuration(courseData.duration)}
                      </span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Giá</span>
                      <span className="font-medium">
                        {courseData.price > 0
                          ? `${courseData.price.toLocaleString("vi-VN")}₫`
                          : "Miễn phí"}
                      </span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Ngày tạo</span>
                      <span className="font-medium">
                        {new Date(courseData.createdAt).toLocaleDateString("vi-VN")}
                      </span>
                    </li>
                    <li className="flex justify-between">
                      <span className="text-foreground/70">Cập nhật</span>
                      <span className="font-medium">
                        {new Date(courseData.updatedAt).toLocaleDateString("vi-VN")}
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

              <div>
                {(!topicData || topicData.length === 0) ? (
                  <div className="text-center py-10 text-foreground/70">
                    Chưa có chủ đề nào cho khóa học này.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {topicData.map((topic, idx: number) => (
                      <details
                        key={topic.order}
                        className="group bg-foreground/5 rounded-xl overflow-hidden"
                        open={idx === 0}>
                        <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-foreground/10">
                          <div>
                            <h3 className="font-medium">
                              Chủ đề {topic.order}: {topic.name}
                            </h3>
                            <p className="text-sm text-foreground/70 mt-1">
                              {topic.description}
                            </p>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-sm text-foreground/70">
                              {topic.lessons?.length || 0} bài học
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
                          {topic.lessons?.map((lesson) => (
                            <div
                              key={lesson.id}
                              className="flex items-center gap-4 p-4 hover:bg-foreground/5">
                              <div className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center bg-blue-500/10 text-blue-500">
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
                              </div>
                              <div className="flex-grow">
                                <div className="flex items-center gap-2">
                                  <h4 className="font-medium">{lesson.title}</h4>
                                  {lesson.sections && lesson.sections.length > 0 && (
                                    <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                                      {lesson.sections.length} phần
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm text-foreground/70 mt-1">
                                  {lesson.description}
                                </p>
                                {lesson.sections && lesson.sections.length > 0 && (
                                  <div className="mt-2">
                                    <p className="text-xs text-foreground/60">
                                      Các phần: {lesson.sections.map((section: any) => section.title).join(", ")}
                                    </p>
                                  </div>
                                )}
                              </div>
                              <div className="flex items-center gap-3 flex-shrink-0">
                                {lesson.isCompleted ? (
                                  <span className="px-3 py-1 text-sm bg-primary text-white rounded border border-green-200">
                                    Đã xong
                                  </span>
                                ) : (
                                  <Link
                                    href={`/lessons/${lesson.id}`}
                                    className="px-3 py-1 text-sm border border-primary text-primary rounded hover:bg-primary/10 transition">
                                    Học ngay
                                  </Link>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      </details>
                    ))}
                  </div>
                )}
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
