"use client";

import React, { useState } from "react";
import { Tabs } from "@mantine/core";

/**
 * Trang cài đặt người dùng
 * Hiển thị các tùy chọn cài đặt cho tài khoản, giao diện, thông báo và riêng tư
 */
const SettingsPage = () => {
  // State để theo dõi trạng thái các tùy chọn
  const [notifications, setNotifications] = useState({
    email: true,
    browser: true,
    updates: false,
    marketing: false,
  });

  const [preferences, setPreferences] = useState({
    exerciseDifficulty: "medium",
    showSolutions: true,
    codeEditorTheme: "dark",
    codeEditorFontSize: "14px",
  });

  const [privacy, setPrivacy] = useState({
    profileVisibility: "public",
    showProgress: true,
    showActivity: true,
    allowDataCollection: true,
  });

  // Xử lý thay đổi tùy chọn thông báo
  const handleNotificationChange = (key: keyof typeof notifications) => {
    setNotifications((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Xử lý thay đổi tùy chọn riêng tư
  const handlePrivacyChange = (key: keyof typeof privacy) => {
    if (key === "profileVisibility") return; // Xử lý riêng cho select
    setPrivacy((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <h1 className="text-2xl font-bold text-foreground mb-6">Cài đặt</h1>

      <Tabs defaultValue="appearance" color="blue" radius="md">
        <Tabs.List className="mb-6">
          <Tabs.Tab value="appearance">Giao diện</Tabs.Tab>
          <Tabs.Tab value="notifications">Thông báo</Tabs.Tab>
          <Tabs.Tab value="preferences">Tùy chỉnh</Tabs.Tab>
          <Tabs.Tab value="privacy">Riêng tư</Tabs.Tab>
        </Tabs.List>

        {/* Cài đặt giao diện */}
        <Tabs.Panel value="appearance" className="space-y-6">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Giao diện
            </h2>

            <div className="space-y-6">
              {/* Chế độ giao diện */}
              <div>
                <h3 className="text-lg font-medium mb-3 text-foreground">
                  Chế độ
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="border border-foreground/10 rounded-lg p-4 cursor-pointer hover:border-primary transition-colors">
                    <div className="h-24 bg-white rounded mb-3 flex items-center justify-center border border-gray-200">
                      <span className="text-black">Aa</span>
                    </div>
                    <p className="font-medium text-center">Sáng</p>
                  </div>

                  <div className="border border-foreground/10 rounded-lg p-4 cursor-pointer hover:border-primary transition-colors">
                    <div className="h-24 bg-black rounded mb-3 flex items-center justify-center border border-gray-800">
                      <span className="text-white">Aa</span>
                    </div>
                    <p className="font-medium text-center">Tối</p>
                  </div>

                  <div className="border border-primary rounded-lg p-4 cursor-pointer relative">
                    <div className="h-24 bg-gradient-to-r from-gray-100 to-gray-100 dark:from-gray-900 dark:to-gray-900 rounded mb-3 flex items-center justify-center">
                      <span>Aa</span>
                    </div>
                    <p className="font-medium text-center">Theo hệ thống</p>
                    <div className="absolute top-2 right-2 text-primary">✓</div>
                  </div>
                </div>
              </div>

              {/* Màu chủ đạo */}
              <div>
                <h3 className="text-lg font-medium mb-3 text-foreground">
                  Màu chủ đạo
                </h3>
                <div className="grid grid-cols-3 sm:grid-cols-6 gap-4">
                  <div className="aspect-square bg-blue-500 rounded-full cursor-pointer border-2 border-transparent hover:border-white transition-colors"></div>
                  <div className="aspect-square bg-purple-500 rounded-full cursor-pointer border-2 border-transparent hover:border-white transition-colors"></div>
                  <div className="aspect-square bg-pink-500 rounded-full cursor-pointer border-2 border-transparent hover:border-white transition-colors"></div>
                  <div className="aspect-square bg-orange-500 rounded-full cursor-pointer border-2 border-transparent hover:border-white transition-colors"></div>
                  <div className="aspect-square bg-green-500 rounded-full cursor-pointer border-2 border-transparent hover:border-white transition-colors"></div>
                  <div className="aspect-square bg-primary rounded-full cursor-pointer border-2 border-white transition-colors"></div>
                </div>
              </div>

              {/* Font chữ */}
              <div>
                <h3 className="text-lg font-medium mb-3 text-foreground">
                  Font chữ
                </h3>
                <div className="max-w-md">
                  <select className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition">
                    <option value="system">Mặc định hệ thống</option>
                    <option value="inter">Inter</option>
                    <option value="roboto">Roboto</option>
                    <option value="opensans">Open Sans</option>
                    <option value="montserrat">Montserrat</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <button className="bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors">
                Lưu thay đổi
              </button>
            </div>
          </div>
        </Tabs.Panel>

        {/* Cài đặt thông báo */}
        <Tabs.Panel value="notifications" className="space-y-6">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Thông báo
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between py-2">
                <div>
                  <h3 className="font-medium text-foreground">
                    Thông báo qua Email
                  </h3>
                  <p className="text-sm text-foreground/60">
                    Gửi email khi có bài học hoặc bài tập mới
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={notifications.email}
                    onChange={() => handleNotificationChange("email")}
                  />
                  <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="border-t border-foreground/10"></div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <h3 className="font-medium text-foreground">
                    Thông báo trình duyệt
                  </h3>
                  <p className="text-sm text-foreground/60">
                    Hiển thị thông báo trên trình duyệt
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={notifications.browser}
                    onChange={() => handleNotificationChange("browser")}
                  />
                  <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="border-t border-foreground/10"></div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <h3 className="font-medium text-foreground">
                    Cập nhật sản phẩm
                  </h3>
                  <p className="text-sm text-foreground/60">
                    Nhận thông báo về các tính năng mới
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={notifications.updates}
                    onChange={() => handleNotificationChange("updates")}
                  />
                  <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="border-t border-foreground/10"></div>

              <div className="flex items-center justify-between py-2">
                <div>
                  <h3 className="font-medium text-foreground">Marketing</h3>
                  <p className="text-sm text-foreground/60">
                    Nhận email về khóa học và ưu đãi
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={notifications.marketing}
                    onChange={() => handleNotificationChange("marketing")}
                  />
                  <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>
            </div>
          </div>
        </Tabs.Panel>

        {/* Cài đặt tùy chỉnh */}
        <Tabs.Panel value="preferences" className="space-y-6">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Tùy chỉnh học tập
            </h2>

            <div className="space-y-6 max-w-xl">
              <div>
                <label className="block text-foreground font-medium mb-2">
                  Mức độ khó mặc định của bài tập
                </label>
                <select
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                  value={preferences.exerciseDifficulty}
                  onChange={(e) =>
                    setPreferences({
                      ...preferences,
                      exerciseDifficulty: e.target.value,
                    })
                  }
                >
                  <option value="easy">Dễ</option>
                  <option value="medium">Trung bình</option>
                  <option value="hard">Khó</option>
                  <option value="mixed">Hỗn hợp</option>
                </select>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-foreground">
                    Hiển thị lời giải sau khi hoàn thành
                  </h3>
                  <p className="text-sm text-foreground/60">
                    Cho phép xem lời giải khi hoàn thành bài tập
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={preferences.showSolutions}
                    onChange={() =>
                      setPreferences({
                        ...preferences,
                        showSolutions: !preferences.showSolutions,
                      })
                    }
                  />
                  <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div>
                <label className="block text-foreground font-medium mb-2">
                  Theme trình soạn thảo mã
                </label>
                <select
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                  value={preferences.codeEditorTheme}
                  onChange={(e) =>
                    setPreferences({
                      ...preferences,
                      codeEditorTheme: e.target.value,
                    })
                  }
                >
                  <option value="light">Sáng</option>
                  <option value="dark">Tối</option>
                  <option value="system">Theo hệ thống</option>
                </select>
              </div>

              <div>
                <label className="block text-foreground font-medium mb-2">
                  Cỡ chữ trình soạn thảo mã
                </label>
                <select
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                  value={preferences.codeEditorFontSize}
                  onChange={(e) =>
                    setPreferences({
                      ...preferences,
                      codeEditorFontSize: e.target.value,
                    })
                  }
                >
                  <option value="12px">12px</option>
                  <option value="14px">14px</option>
                  <option value="16px">16px</option>
                  <option value="18px">18px</option>
                  <option value="20px">20px</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <button className="bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors">
                Lưu thay đổi
              </button>
            </div>
          </div>
        </Tabs.Panel>

        {/* Cài đặt riêng tư */}
        <Tabs.Panel value="privacy" className="space-y-6">
          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-6 text-foreground">
              Cài đặt riêng tư
            </h2>

            <div className="space-y-6 max-w-xl">
              <div>
                <label className="block text-foreground font-medium mb-2">
                  Chế độ hồ sơ
                </label>
                <select
                  className="w-full p-2 border border-foreground/20 rounded-lg bg-background theme-transition"
                  value={privacy.profileVisibility}
                  onChange={(e) =>
                    setPrivacy({
                      ...privacy,
                      profileVisibility: e.target.value,
                    })
                  }
                >
                  <option value="public">Công khai</option>
                  <option value="private">Riêng tư</option>
                  <option value="friends">Chỉ bạn bè</option>
                </select>
                <p className="text-sm text-foreground/60 mt-1">
                  Chế độ công khai cho phép mọi người xem hồ sơ của bạn
                </p>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-foreground">
                    Hiển thị tiến độ học tập
                  </h3>
                  <p className="text-sm text-foreground/60">
                    Cho phép người khác xem tiến độ học tập của bạn
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={privacy.showProgress}
                    onChange={() => handlePrivacyChange("showProgress")}
                  />
                  <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium text-foreground">
                    Hiển thị hoạt động gần đây
                  </h3>
                  <p className="text-sm text-foreground/60">
                    Hiển thị các hoạt động gần đây của bạn cho người khác
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={privacy.showActivity}
                    onChange={() => handlePrivacyChange("showActivity")}
                  />
                  <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
              </div>

              <div className="border-t border-foreground/10 pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-foreground">
                      Thu thập dữ liệu
                    </h3>
                    <p className="text-sm text-foreground/60">
                      Cho phép thu thập dữ liệu để cải thiện trải nghiệm
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={privacy.allowDataCollection}
                      onChange={() =>
                        handlePrivacyChange("allowDataCollection")
                      }
                    />
                    <div className="w-11 h-6 bg-foreground/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-foreground/20 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <button className="bg-primary text-white px-4 py-2 rounded-lg font-medium hover:bg-primary/90 transition-colors">
                Lưu thay đổi
              </button>
            </div>
          </div>

          <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
            <h2 className="text-xl font-semibold mb-4 text-foreground">
              Quản lý dữ liệu
            </h2>
            <p className="text-foreground/70 mb-4">
              Bạn có thể tải xuống hoặc xóa tất cả dữ liệu của mình.
            </p>

            <div className="flex gap-4">
              <button className="bg-foreground/10 text-foreground px-4 py-2 rounded-lg font-medium hover:bg-foreground/20 transition-colors">
                Tải xuống dữ liệu
              </button>
              <button className="bg-red-500/10 text-red-500 px-4 py-2 rounded-lg font-medium hover:bg-red-500/20 transition-colors">
                Xóa tất cả dữ liệu
              </button>
            </div>
          </div>
        </Tabs.Panel>
      </Tabs>
    </div>
  );
};

export default SettingsPage;
