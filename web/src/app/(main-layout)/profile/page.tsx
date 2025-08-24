"use client";

import React from "react";
import { Tabs } from "@mantine/core";
import Image from "next/image";
import { Skeleton } from "@mantine/core";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { profileApi, CourseProgress, Badge, Activity } from "@/lib/api/profile";

/**
 * Trang hồ sơ người dùng
 * Hiển thị thông tin cá nhân, tiến độ học tập, thành tích, lịch sử hoạt động
 */
const ProfilePage = () => {
  // Sử dụng React Query để lấy và cache dữ liệu profile
  const {
    data: profile,
    isLoading,
    error
  } = useQuery({
    queryKey: ['profile'],
    queryFn: profileApi.getProfile,
    staleTime: 5 * 60 * 1000, // 5 phút
    retry: 1,
  });

  if (isLoading) {
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

  if (error || !profile) {
    return (
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="bg-background rounded-xl shadow-sm p-6 text-center">
          <h1 className="text-2xl font-bold mb-4">Không thể tải thông tin hồ sơ</h1>
          <p className="mb-6 text-foreground/70">
            Đã xảy ra lỗi khi tải thông tin hồ sơ của bạn. Vui lòng thử lại sau.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      {/* Header của profile */}
      <div className="bg-background rounded-xl shadow-sm p-6 mb-6 border border-foreground/10 flex flex-col md:flex-row gap-6 items-center md:items-start theme-transition">
        {/* Avatar */}
        <div className="relative">
          <div className="w-28 h-28 rounded-full overflow-hidden bg-gradient-to-br from-primary/20 to-secondary/20 flex items-center justify-center border-4 border-background shadow-lg">
            {profile.avatar ? (
              <Image
                src={profile.avatar}
                alt={profile.fullName}
                width={100}
                height={100}
                className="object-cover"
              />
            ) : (
              <span className="text-4xl">{profile.fullName.charAt(0)}</span>
            )}
          </div>
          <span className="absolute -bottom-2 -right-2 bg-primary text-white text-xs font-bold rounded-full w-8 h-8 flex items-center justify-center shadow-md">
            Lv{profile.stats.level}
          </span>
        </div>

        {/* Thông tin cơ bản */}
        <div className="flex-1 text-center md:text-left">
          <h1 className="text-2xl font-bold text-foreground">
            {profile.fullName}
          </h1>
          <p className="text-foreground/60 mb-3">@{profile.username}</p>
          <p className="text-foreground/80 mb-4 max-w-2xl">{profile.bio}</p>

          {/* Stats grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-2">
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">
                Bài tập đã hoàn thành
              </p>
              <p className="text-xl font-semibold">
                {profile.stats.completedExercises}
              </p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">
                Khóa học đã hoàn thành
              </p>
              <p className="text-xl font-semibold">
                {profile.stats.completedCourses}
              </p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">Tổng điểm</p>
              <p className="text-xl font-semibold">{profile.stats.totalPoints}</p>
            </div>
            <div className="bg-background/50 p-3 rounded-lg border border-foreground/10 theme-transition">
              <p className="text-foreground/60 text-xs">Chuỗi hoạt động</p>
              <p className="text-xl font-semibold flex items-center gap-1">
                {profile.stats.streak} <span className="text-amber-500">🔥</span>
              </p>
            </div>
          </div>
        </div>

        {/* Nút chỉnh sửa profile */}
        <button
          onClick={() =>
            alert("Tính năng chỉnh sửa hồ sơ đang được phát triển!")
          }
          className="bg-background border border-foreground/10 hover:bg-foreground/5 text-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors theme-transition">
          Chỉnh sửa hồ sơ
        </button>
      </div>

      {/* Tabs cho các phần nội dung khác nhau */}
      <Tabs
        defaultValue="overview"
        color="rgb(var(--color-primary))"
        radius="md">
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
                    {profile.learningProgress.algorithms}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${profile.learningProgress.algorithms}%`,
                    }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-foreground/80">
                    Cấu trúc dữ liệu
                  </span>
                  <span className="text-sm font-medium text-foreground/80">
                    {profile.learningProgress.dataStructures}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${profile.learningProgress.dataStructures}%`,
                    }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-foreground/80">
                    Lập trình động
                  </span>
                  <span className="text-sm font-medium text-foreground/80">
                    {profile.learningProgress.dynamicProgramming}%
                  </span>
                </div>
                <div className="w-full bg-foreground/10 rounded-full h-2.5">
                  <div
                    className="bg-primary h-2.5 rounded-full"
                    style={{
                      width: `${profile.learningProgress.dynamicProgramming}%`,
                    }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Khóa học đang tham gia */}
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-foreground">
                Khóa học đang tham gia
              </h2>
              <Link
                href="/courses"
                className="text-primary hover:underline text-sm font-medium"
              >
                Xem tất cả
              </Link>
            </div>
            {profile.courses.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {profile.courses.map((course: CourseProgress) => (
                  <div
                    key={course.id}
                    className="border border-foreground/10 rounded-lg overflow-hidden hover:shadow-md transition-shadow bg-background/50 theme-transition">
                    <div
                      className={`h-40 bg-gradient-to-r from-${course.colorFrom} to-${course.colorTo} relative`}>
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
                          style={{ width: `${course.progress}%` }}></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-foreground/60 mb-4">
                  Bạn chưa tham gia khóa học nào
                </p>
                <Link
                  href="/courses"
                  className="bg-primary text-white px-4 py-2 rounded-lg hover:opacity-90 transition"
                >
                  Khám phá khóa học
                </Link>
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

            {profile.badges.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                {profile.badges.map((badge: Badge) => (
                  <div
                    key={badge.id}
                    className={`border ${badge.unlocked
                      ? "border-amber-200 bg-amber-50/50"
                      : "border-foreground/10 bg-background/50 opacity-50"
                      } rounded-lg p-4 text-center transition-all hover:shadow-md flex flex-col items-center justify-center gap-2`}>
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

            {profile.activities.length > 0 ? (
              <div className="space-y-4">
                {profile.activities.map((activity: Activity) => (
                  <div
                    key={activity.id}
                    className="border-l-4 border-primary pl-4 py-2">
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
                      defaultValue={profile.fullName}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground/70 mb-1">
                      Giới thiệu bản thân
                    </label>
                    <textarea
                      className="w-full p-2 border border-foreground/10 rounded-lg bg-background theme-transition"
                      rows={3}
                      defaultValue={profile.bio}></textarea>
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
