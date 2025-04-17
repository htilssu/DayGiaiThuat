"use client";

import React, { useState, useEffect } from "react";
import { Tabs } from "@mantine/core";
import Image from "next/image";
import { useAuth } from "@/contexts/AuthContext";
import profileService, { ProfileData } from "@/services/profile.service";
import { Skeleton } from "@mantine/core";

/**
 * Trang hồ sơ người dùng
 * Hiển thị thông tin cá nhân, tiến độ học tập, thành tích, lịch sử hoạt động
 */
const ProfilePage = () => {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProfile = async () => {
      if (!isAuthenticated || !user) return;

      try {
        setIsLoading(true);
        const data = await profileService.getProfile(user.id);
        setProfileData(data);
        setError(null);
      } catch (err) {
        console.error("Lỗi khi tải thông tin profile:", err);
        setError("Không thể tải thông tin hồ sơ. Vui lòng thử lại sau.");
      } finally {
        setIsLoading(false);
      }
    };

    loadProfile();
  }, [user, isAuthenticated]);

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

  if (error) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 flex flex-col items-center justify-center">
          <div className="text-red-500 text-xl mb-4">⚠️ {error}</div>
          <button
            onClick={() => window.location.reload()}
            className="bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors"
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  if (!profileData) {
    return null;
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header của profile */}
      <div className="bg-background rounded-xl shadow-sm p-6 mb-6 border border-foreground/10 flex flex-col md:flex-row gap-6 items-center md:items-start theme-transition">
        {/* Avatar */}
        <div className="relative">
          <div className="w-28 h-28 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center border-4 border-background shadow-lg">
            {profileData.avatar ? (
              <Image
                src={profileData.avatar}
                alt={profileData.fullName}
                width={100}
                height={100}
                className="object-cover"
              />
            ) : (
              <span className="text-4xl">{profileData.fullName.charAt(0)}</span>
            )}
          </div>
          <span className="absolute -bottom-2 -right-2 bg-primary text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-md">
            Lv{profileData.stats.level}
          </span>
        </div>

        {/* Thông tin cơ bản */}
        <div className="flex-1 text-center md:text-left">
          <h1 className="text-2xl font-bold text-foreground">
            {profileData.fullName}
          </h1>
          <p className="text-foreground/60 mb-3">@{profileData.username}</p>
          <p className="text-foreground/80 mb-4 max-w-2xl">{profileData.bio}</p>

          {/* Stats grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2">
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">
                Bài tập đã hoàn thành
              </p>
              <p className="text-xl font-semibold">
                {profileData.stats.completedExercises}
              </p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">
                Khóa học đã hoàn thành
              </p>
              <p className="text-xl font-semibold">
                {profileData.stats.completedCourses}
              </p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">Tổng điểm</p>
              <p className="text-xl font-semibold">
                {profileData.stats.totalPoints}
              </p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">Chuỗi hoạt động</p>
              <p className="text-xl font-semibold flex items-center gap-1">
                {profileData.stats.streak}{" "}
                <span className="text-amber-500">🔥</span>
              </p>
            </div>
          </div>
        </div>

        {/* Nút chỉnh sửa profile */}
        <button className="bg-background border border-foreground/10 hover:bg-foreground/5 text-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors theme-transition">
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
                    {profileData.learningProgress.algorithms}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${profileData.learningProgress.algorithms}%`,
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
                    {profileData.learningProgress.dataStructures}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${profileData.learningProgress.dataStructures}%`,
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
                    {profileData.learningProgress.dynamicProgramming}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${profileData.learningProgress.dynamicProgramming}%`,
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
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {profileData.courses.map((course) => (
                <div
                  key={course.id}
                  className="border border-foreground/10 rounded-lg overflow-hidden hover:shadow-md transition-shadow bg-background/50 theme-transition"
                >
                  <div
                    className={`h-40 bg-gradient-to-r from-${course.colorFrom} to-${course.colorTo} relative`}
                  >
                    <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/70 to-transparent">
                      <h3 className="text-white font-medium">{course.name}</h3>
                    </div>
                  </div>
                  <div className="p-4">
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-foreground/80">
                        Tiến độ
                      </span>
                      <span className="text-sm text-foreground/80">
                        {course.progress}%
                      </span>
                    </div>
                    <div className="w-full bg-foreground/10 rounded-full h-1.5 mb-3">
                      <div
                        className="bg-primary h-1.5 rounded-full"
                        style={{ width: `${course.progress}%` }}
                      ></div>
                    </div>
                    <button className="w-full py-1.5 bg-primary/10 text-primary hover:bg-primary/20 rounded text-sm font-medium transition-colors">
                      Tiếp tục học
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Tabs.Panel>

        {/* Nội dung tab Thành tích */}
        <Tabs.Panel value="achievements" className="space-y-6">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Huy hiệu đạt được
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {profileData.badges
                .filter((badge) => badge.unlocked)
                .map((badge) => (
                  <div
                    key={badge.id}
                    className="flex items-center gap-4 p-4 border border-foreground/10 rounded-lg bg-background/50 hover:shadow-sm transition-shadow theme-transition"
                  >
                    <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center text-2xl">
                      {badge.icon}
                    </div>
                    <div>
                      <h3 className="font-medium text-foreground">
                        {badge.name}
                      </h3>
                      <p className="text-sm text-foreground/60">
                        {badge.description}
                      </p>
                    </div>
                  </div>
                ))}
              {/* Huy hiệu khóa - chưa đạt được */}
              {profileData.badges
                .filter((badge) => !badge.unlocked)
                .map((badge) => (
                  <div
                    key={badge.id}
                    className="flex items-center gap-4 p-4 border border-foreground/10 rounded-lg bg-background/50 opacity-50 theme-transition"
                  >
                    <div className="w-12 h-12 bg-foreground/10 rounded-full flex items-center justify-center text-2xl">
                      {badge.icon}
                    </div>
                    <div>
                      <h3 className="font-medium text-foreground">
                        {badge.name}
                      </h3>
                      <p className="text-sm text-foreground/60">
                        {badge.description}
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </div>

          {/* Thống kê */}
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Thống kê
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium mb-3 text-foreground">
                  Phân bố bài tập
                </h3>
                <div className="h-64 bg-foreground/5 rounded-lg p-4 flex items-end justify-between gap-2">
                  <div className="flex flex-col items-center gap-2">
                    <div
                      className="w-12 bg-green-500 rounded-t"
                      style={{ height: "40%" }}
                    ></div>
                    <span className="text-xs">Dễ</span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <div
                      className="w-12 bg-yellow-500 rounded-t"
                      style={{ height: "70%" }}
                    ></div>
                    <span className="text-xs">TB</span>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <div
                      className="w-12 bg-red-500 rounded-t"
                      style={{ height: "25%" }}
                    ></div>
                    <span className="text-xs">Khó</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-medium mb-3 text-foreground">
                  Hoạt động hàng tuần
                </h3>
                <div className="h-64 bg-foreground/5 rounded-lg p-4 grid grid-cols-7 gap-1 items-end">
                  {["T2", "T3", "T4", "T5", "T6", "T7", "CN"].map((day, i) => (
                    <div key={day} className="flex flex-col items-center gap-2">
                      <div
                        className="w-full bg-primary rounded-t"
                        style={{ height: `${Math.random() * 80 + 10}%` }}
                      ></div>
                      <span className="text-xs">{day}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </Tabs.Panel>

        {/* Nội dung tab Hoạt động */}
        <Tabs.Panel value="activity" className="space-y-6">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Hoạt động gần đây
            </h2>
            <div className="space-y-4">
              {profileData.activities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex gap-4 p-4 border-b border-foreground/10 last:border-0"
                >
                  <div className="w-10 h-10 rounded-full flex items-center justify-center bg-primary/10 text-primary flex-shrink-0">
                    {activity.type === "exercise" && "📝"}
                    {activity.type === "course" && "📚"}
                    {activity.type === "discussion" && "💬"}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between">
                      <h3 className="font-medium text-foreground">
                        {activity.name}
                      </h3>
                      <span className="text-sm text-foreground/60">
                        {activity.date}
                      </span>
                    </div>
                    <p className="text-sm text-foreground/80">
                      {activity.type === "exercise" &&
                        `Hoàn thành bài tập với điểm số ${activity.score}`}
                      {activity.type === "course" &&
                        `Tiến độ khóa học: ${activity.progress}`}
                      {activity.type === "discussion" && "Tham gia thảo luận"}
                    </p>
                  </div>
                </div>
              ))}
            </div>
            <button className="mt-4 text-primary hover:text-primary/80 text-sm font-medium transition-colors">
              Xem tất cả hoạt động
            </button>
          </div>

          {/* Lịch hoạt động */}
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Lịch hoạt động
            </h2>
            <div className="grid grid-cols-7 gap-1 mb-4">
              {["CN", "T2", "T3", "T4", "T5", "T6", "T7"].map((day) => (
                <div
                  key={day}
                  className="text-center text-sm font-medium text-foreground/70"
                >
                  {day}
                </div>
              ))}
              {Array.from({ length: 35 }).map((_, i) => (
                <div
                  key={i}
                  className={`w-full aspect-square rounded-sm border ${
                    Math.random() > 0.7
                      ? "bg-primary/20 border-primary/30"
                      : "bg-foreground/5 border-foreground/10"
                  }`}
                ></div>
              ))}
            </div>
            <div className="flex justify-between items-center text-xs text-foreground/70">
              <span>Ít</span>
              <div className="flex gap-1">
                <div className="w-3 h-3 bg-foreground/5 border-foreground/10 border rounded-sm"></div>
                <div className="w-3 h-3 bg-primary/10 border-primary/20 border rounded-sm"></div>
                <div className="w-3 h-3 bg-primary/30 border-primary/40 border rounded-sm"></div>
                <div className="w-3 h-3 bg-primary/60 border-primary/70 border rounded-sm"></div>
                <div className="w-3 h-3 bg-primary border-primary border rounded-sm"></div>
              </div>
              <span>Nhiều</span>
            </div>
          </div>
        </Tabs.Panel>

        {/* Nội dung tab Cài đặt */}
        <Tabs.Panel value="settings" className="space-y-6">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Thông tin tài khoản
            </h2>
            <div className="space-y-4 max-w-md">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">
                  Họ và tên
                </label>
                <input
                  type="text"
                  defaultValue={profileData.fullName}
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">
                  Tên người dùng
                </label>
                <input
                  type="text"
                  defaultValue={profileData.username}
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  defaultValue={profileData.email}
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">
                  Giới thiệu
                </label>
                <textarea
                  defaultValue={profileData.bio}
                  rows={3}
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                ></textarea>
              </div>
              <div className="pt-2">
                <button className="bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors">
                  Lưu thay đổi
                </button>
              </div>
            </div>
          </div>

          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Bảo mật
            </h2>
            <div className="space-y-4 max-w-md">
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">
                  Mật khẩu hiện tại
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">
                  Mật khẩu mới
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-foreground/80 mb-1">
                  Xác nhận mật khẩu
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                />
              </div>
              <div className="pt-2">
                <button className="bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors">
                  Đổi mật khẩu
                </button>
              </div>
            </div>
          </div>

          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground text-red-500">
              Nguy hiểm
            </h2>
            <p className="text-foreground/70 mb-4">
              Các hành động dưới đây không thể hoàn tác. Hãy cẩn thận!
            </p>
            <button className="bg-red-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-600 transition-colors">
              Xóa tài khoản
            </button>
          </div>
        </Tabs.Panel>
      </Tabs>
    </div>
  );
};

export default ProfilePage;
