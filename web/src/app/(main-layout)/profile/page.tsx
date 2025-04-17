"use client";

import React, { useState, useEffect } from "react";
import { Tabs } from "@mantine/core";
import Image from "next/image";
import { useAuth } from "@/contexts/AuthContext";
import { Skeleton } from "@mantine/core";
import { Activity, Badge, CourseProgress } from "@/services/profile.service";

/**
 * Trang hồ sơ người dùng
 * Hiển thị thông tin cá nhân, tiến độ học tập, thành tích, lịch sử hoạt động
 *
 * Lưu ý: Trang này sử dụng dữ liệu trực tiếp từ AuthContext thay vì gọi API
 * để tối ưu hiệu suất và giảm số lượng request.
 * Dữ liệu người dùng đã được chuyển đổi từ định dạng API sang định dạng thân thiện với frontend.
 */
const ProfilePage = () => {
  // Lấy thông tin người dùng từ AuthContext
  const {
    user,
    isAuthenticated,
    isLoading: authLoading,
    error: authError,
    clearError,
  } = useAuth();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!authLoading) {
      setIsLoading(false);
    }
  }, [authLoading]);

  if (authLoading || isLoading) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-background rounded-xl shadow-sm p-6 mb-6 border border-foreground/10 flex flex-col md:flex-row gap-6 items-center md:items-start">
          <Skeleton height={112} width={112} radius="xl" />
          <div className="flex-1">
            <Skeleton height={32} width={200} radius="md" mb="md" />
            <Skeleton height={20} radius="md" mb="md" />
            <Skeleton height={60} radius="md" mb="md" />
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <Skeleton height={80} radius="md" />
              <Skeleton height={80} radius="md" />
              <Skeleton height={80} radius="md" />
              <Skeleton height={80} radius="md" />
            </div>
          </div>
        </div>

        <Skeleton height={50} radius="md" mb="lg" />
        <Skeleton height={300} radius="md" />
      </div>
    );
  }

  if (authError && !user) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 flex flex-col items-center justify-center">
          <div className="text-red-500 text-xl mb-4">⚠️ {authError}</div>
          <div className="flex space-x-4">
            <button
              onClick={() => window.location.reload()}
              className="bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
            >
              Thử lại
            </button>
            <button
              onClick={clearError}
              className="bg-gray-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-600 transition-colors"
            >
              Bỏ qua
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 flex flex-col items-center justify-center">
          <div className="text-yellow-500 text-xl mb-4">
            ⚠️ Vui lòng đăng nhập để xem trang hồ sơ
          </div>
        </div>
      </div>
    );
  }

  // Hiển thị thông báo lỗi nhẹ nếu cần
  const renderErrorBanner = () => {
    if (authError) {
      return (
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-yellow-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3 flex justify-between w-full">
              <p className="text-sm text-yellow-700">{authError}</p>
              <button
                onClick={clearError}
                className="text-sm text-yellow-700 font-medium hover:text-yellow-800"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Hiển thị banner thông báo lỗi nếu có */}
      {renderErrorBanner()}

      {/* Header của profile */}
      <div className="bg-background rounded-xl shadow-sm p-6 mb-6 border border-foreground/10 flex flex-col md:flex-row gap-6 items-center md:items-start theme-transition">
        {/* Avatar */}
        <div className="relative">
          <div className="w-28 h-28 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center border-4 border-background shadow-lg">
            {user.avatar ? (
              <Image
                src={user.avatar}
                alt={user.fullName}
                width={100}
                height={100}
                className="object-cover"
              />
            ) : (
              <span className="text-4xl">{user.fullName.charAt(0)}</span>
            )}
          </div>
          <span className="absolute -bottom-2 -right-2 bg-primary text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-md">
            Lv{user.stats.level}
          </span>
        </div>

        {/* Thông tin cơ bản */}
        <div className="flex-1 text-center md:text-left">
          <h1 className="text-2xl font-bold text-foreground">
            {user.fullName}
          </h1>
          <p className="text-foreground/60 mb-3">@{user.username}</p>
          <p className="text-foreground/80 mb-4 max-w-2xl">{user.bio}</p>

          {/* Stats grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2">
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">
                Bài tập đã hoàn thành
              </p>
              <p className="text-xl font-semibold">
                {user.stats.completedExercises}
              </p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">
                Khóa học đã hoàn thành
              </p>
              <p className="text-xl font-semibold">
                {user.stats.completedCourses}
              </p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">Tổng điểm</p>
              <p className="text-xl font-semibold">{user.stats.totalPoints}</p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">Chuỗi hoạt động</p>
              <p className="text-xl font-semibold flex items-center gap-1">
                {user.stats.streak} <span className="text-amber-500">🔥</span>
              </p>
            </div>
          </div>
        </div>

        {/* Nút chỉnh sửa profile */}
        <button
          onClick={() =>
            alert("Tính năng chỉnh sửa hồ sơ đang được phát triển!")
          }
          className="bg-background border border-foreground/10 hover:bg-foreground/5 text-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors theme-transition"
        >
          Chỉnh sửa hồ sơ
        </button>
      </div>

      {/* Tabs cho các phần nội dung khác nhau */}
      <Tabs defaultValue="overview" color="blue" radius="md">
        <Tabs.List className="mb-6">
          <Tabs.Tab value="overview">Tổng quan</Tabs.Tab>
          <Tabs.Tab value="achievements">Thành tích</Tabs.Tab>
          <Tabs.Tab value="activity">Hoạt động</Tabs.Tab>
          <Tabs.Tab value="settings">Cài đặt</Tabs.Tab>
        </Tabs.List>

        {/* Nội dung tab Tổng quan */}
        <Tabs.Panel value="overview" className="space-y-6">
          {/* Tiến độ học tập */}
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Tiến độ học tập
            </h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-foreground/80">
                    Thuật toán cơ bản
                  </span>
                  <span className="text-sm font-medium text-foreground/80">
                    {user.learningProgress.algorithms}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${user.learningProgress.algorithms}%`,
                    }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-foreground/80">
                    Cấu trúc dữ liệu
                  </span>
                  <span className="text-sm font-medium text-foreground/80">
                    {user.learningProgress.dataStructures}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${user.learningProgress.dataStructures}%`,
                    }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-foreground/80">
                    Lập trình động
                  </span>
                  <span className="text-sm font-medium text-foreground/80">
                    {user.learningProgress.dynamicProgramming}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${user.learningProgress.dynamicProgramming}%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Khóa học đang tham gia */}
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Khóa học đang tham gia
            </h2>
            {user.courses.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {user.courses.map((course: CourseProgress) => (
                  <div
                    key={course.id}
                    className="border border-foreground/10 rounded-lg overflow-hidden hover:shadow-md transition-shadow bg-background/50 theme-transition"
                  >
                    <div
                      className={`h-40 bg-gradient-to-r from-${course.color_from} to-${course.color_to} relative`}
                    >
                      <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/70 to-transparent">
                        <h3 className="text-white font-medium">
                          {course.name}
                        </h3>
                      </div>
                    </div>
                    <div className="p-4">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-foreground/80">
                          Tiến độ hoàn thành
                        </span>
                        <span className="text-sm font-medium text-foreground/80">
                          {course.progress}%
                        </span>
                      </div>
                      <div className="w-full bg-foreground/10 rounded-full h-2.5">
                        <div
                          className="bg-primary h-2.5 rounded-full"
                          style={{ width: `${course.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-foreground/60">
                <p>Bạn chưa tham gia khóa học nào.</p>
                <button className="mt-4 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
                  Khám phá khóa học
                </button>
              </div>
            )}
          </div>
        </Tabs.Panel>

        {/* Nội dung tab Thành tích */}
        <Tabs.Panel value="achievements">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Huy hiệu và thành tích
            </h2>

            {user.badges.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {user.badges.map((badge: Badge) => (
                  <div
                    key={badge.id}
                    className={`border ${
                      badge.unlocked
                        ? "border-amber-200 bg-amber-50/50"
                        : "border-foreground/10 bg-background/50 opacity-50"
                    } rounded-lg p-4 text-center transition-all hover:shadow-md flex flex-col items-center justify-center gap-2`}
                  >
                    <div className="text-4xl mb-2">{badge.icon}</div>
                    <h3 className="font-semibold">{badge.name}</h3>
                    <p className="text-xs text-foreground/70">
                      {badge.description}
                    </p>
                    {!badge.unlocked && (
                      <span className="text-xs bg-foreground/10 px-2 py-1 rounded-full mt-2">
                        Chưa mở khóa
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-foreground/60">
                <p>
                  Chưa có huy hiệu nào. Hãy hoàn thành các thử thách để nhận huy
                  hiệu!
                </p>
              </div>
            )}
          </div>
        </Tabs.Panel>

        {/* Nội dung tab Hoạt động */}
        <Tabs.Panel value="activity">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Lịch sử hoạt động
            </h2>

            {user.activities.length > 0 ? (
              <div className="space-y-4">
                {user.activities.map((activity: Activity) => (
                  <div
                    key={activity.id}
                    className="border-l-4 border-primary pl-4 py-2"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{activity.name}</h3>
                        <p className="text-sm text-foreground/60 mt-1">
                          {activity.type === "exercise"
                            ? "Bài tập"
                            : activity.type === "course"
                            ? "Khóa học"
                            : "Thảo luận"}
                        </p>
                      </div>
                      <div className="text-right">
                        <span className="text-sm text-foreground/60">
                          {activity.date}
                        </span>
                        {activity.score && (
                          <p className="text-sm font-medium text-green-600">
                            Điểm: {activity.score}
                          </p>
                        )}
                        {activity.progress && (
                          <p className="text-sm text-foreground/80">
                            Tiến độ: {activity.progress}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-foreground/60">
                <p>Chưa có hoạt động nào được ghi nhận.</p>
              </div>
            )}
          </div>
        </Tabs.Panel>

        {/* Nội dung tab Cài đặt */}
        <Tabs.Panel value="settings">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Cài đặt tài khoản
            </h2>

            {/* Cài đặt cơ bản */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Thông tin cá nhân</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground/70 mb-1">
                      Họ và tên
                    </label>
                    <input
                      type="text"
                      className="w-full p-2 border border-foreground/10 rounded-lg bg-background theme-transition"
                      defaultValue={user.fullName}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground/70 mb-1">
                      Giới thiệu bản thân
                    </label>
                    <textarea
                      className="w-full p-2 border border-foreground/10 rounded-lg bg-background theme-transition"
                      rows={3}
                      defaultValue={user.bio}
                    ></textarea>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-4">Bảo mật</h3>
                <button className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
                  Đổi mật khẩu
                </button>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-4 text-red-600">
                  Vùng nguy hiểm
                </h3>
                <button className="px-4 py-2 bg-red-500 text-white rounded-lg text-sm font-medium hover:bg-red-600 transition-colors">
                  Xóa tài khoản
                </button>
              </div>
            </div>
          </div>
        </Tabs.Panel>
      </Tabs>
    </div>
  );
};

export default ProfilePage;
