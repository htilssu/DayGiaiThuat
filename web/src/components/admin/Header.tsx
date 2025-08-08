"use client";

import {
  ActionIcon,
  Group,
  Title,
  NavLink,
  Stack,
  Button,
} from "@mantine/core";
import {
  IconMoonStars,
  IconSun,
  IconChartBar,
  IconUsers,
  IconMessage,
  IconUpload,
  IconHome,
  IconLogin,
  IconLogout,
} from "@tabler/icons-react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAppDispatch, useAppSelector } from "@/lib/store";
import { removeUser } from "@/lib/store/userStore";
import { authApi } from "@/lib/api";

export function AdminHeader() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const pathname = usePathname();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.user);

  useEffect(() => {
    // Get initial theme from localStorage or system preference
    const savedTheme = localStorage.getItem("theme") as "light" | "dark";
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute("data-theme", savedTheme);
    } else {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      setTheme(systemTheme);
      document.documentElement.setAttribute("data-theme", systemTheme);
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      dispatch(removeUser());
      router.push("/auth/login");
    } catch (error) {
      console.error("Lỗi đăng xuất:", error);
      // Even if logout API fails, remove user from store and redirect
      dispatch(removeUser());
      router.push("/auth/login");
    }
  };

  const navigationItems = [
    {
      label: "Dashboard",
      href: "/admin",
      icon: IconHome,
      description: "Trang chủ quản trị",
    },
    // {
    //   label: "Tổng quan",
    //   href: "/admin/overview",
    //   icon: IconChartBar,
    //   description: "Thống kê hệ thống",
    // },
    {
      label: "Người dùng",
      href: "/admin/users",
      icon: IconUsers,
      description: "Quản lý người dùng",
    },
    {
      label: "AI Assistant",
      href: "/admin/ai-assistant",
      icon: IconMessage,
      description: "Trợ lý AI",
    },
    {
      label: "Tài liệu",
      href: "/admin/documents",
      icon: IconUpload,
      description: "Upload tài liệu",
    },
  ];

  const renderAuthButton = () => {
    if (user) {
      // User is logged in - show logout button
      return (
        <Button
          variant="light"
          size="sm"
          leftSection={<IconLogout size={16} stroke={1.5} />}
          className="bg-red-500/10 text-red-600 hover:bg-red-500/20"
          onClick={handleLogout}>
          Đăng xuất
        </Button>
      );
    } else {
      // User is not logged in - show login button
      return (
        <Link href="/auth/login">
          <Button
            variant="light"
            size="sm"
            leftSection={<IconLogin size={16} stroke={1.5} />}
            className="bg-primary/10 text-primary hover:bg-primary/20">
            Đăng nhập
          </Button>
        </Link>
      );
    }
  };

  return (
    <header className="border-b border-primary/10 bg-primary/5">
      <div className="container mx-auto px-4 sm:px-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between py-4">
          {/* Header Title and Theme Toggle */}
          <div className="flex items-center justify-between lg:justify-start gap-4 mb-4 lg:mb-0">
            <div className="flex items-center gap-x-3">
              <Title order={3} className="font-semibold">
                Admin Dashboard
              </Title>
            </div>

            {/* <div className="flex items-center gap-x-4 lg:hidden">
              {renderAuthButton()}
              <ActionIcon
                variant="light"
                size="lg"
                className="bg-primary/10 text-primary hover:bg-primary/20"
                onClick={toggleTheme}
                aria-label="Toggle theme">
                {theme === "dark" ? (
                  <IconSun size={20} stroke={1.5} />
                ) : (
                  <IconMoonStars size={20} stroke={1.5} />
                )}
              </ActionIcon>
            </div> */}
          </div>

          {/* Navigation */}
          <nav className="flex-1 lg:flex lg:justify-center">
            <div className="flex flex-wrap gap-2 lg:gap-4">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href;

                return (
                  <Link key={item.href} href={item.href}>
                    <div
                      className={`
                        flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200
                        ${
                          isActive
                            ? "bg-primary text-white shadow-sm"
                            : "text-muted-foreground hover:bg-primary/10 hover:text-primary"
                        }
                      `}
                      title={item.description}>
                      <Icon size={16} stroke={1.5} />
                      <span className="hidden sm:inline">{item.label}</span>
                    </div>
                  </Link>
                );
              })}
            </div>
          </nav>

          {/* Theme Toggle and Auth Button - Desktop */}
          <div className="hidden lg:flex items-center gap-x-4">
            {renderAuthButton()}
            <ActionIcon
              variant="light"
              size="lg"
              className="bg-primary/10 text-primary hover:bg-primary/20"
              onClick={toggleTheme}
              aria-label="Toggle theme">
              {theme === "dark" ? (
                <IconSun size={20} stroke={1.5} />
              ) : (
                <IconMoonStars size={20} stroke={1.5} />
              )}
            </ActionIcon>
          </div>
        </div>
      </div>
    </header>
  );
}
