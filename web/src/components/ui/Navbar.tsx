"use client";

import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import ThemeToggle from "@/components/ui/ThemeToggle";
import { useAppDispatch, useAppSelector } from "@/lib/store";
import { removeUser } from "@/lib/store/userStore";
import { authApi } from "@/lib/api";
import WebSocketStatus from "./WebSocketStatus";
/**
 * Component Navbar chứa menu điều hướng và các tùy chọn người dùng
 * @returns {React.ReactNode} Navbar component
 */
export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [scrollY, setScrollY] = useState(0);
  const pathname = usePathname();
  const userMenuRef = useRef<HTMLDivElement>(null);

  // App name from environment variable
  const appName = process.env.NEXT_PUBLIC_APP_NAME || "AIGiảiThuật";
  const dispatch = useAppDispatch();
  const { user } = useAppSelector((state) => state.user);
  // Theo dõi scroll và lưu giá trị chính xác thay vì boolean
  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };

    // Thiết lập giá trị ban đầu
    setScrollY(window.scrollY);

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Xử lý close menu khi click bên ngoài
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        userMenuRef.current &&
        !userMenuRef.current.contains(event.target as Node)
      ) {
        setIsUserMenuOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Tính toán các giá trị dựa trên scrollY
  const scrollProgress = Math.min(scrollY / 100, 1);
  const backdropBlur = Math.min(8 + scrollProgress * 8, 16); // Từ 8px đến 16px
  const shadowOpacity = scrollProgress * 0.1; // Từ 0 đến 0.1

  // Chỉ hiển thị shadow khi đã cuộn xuống đủ xa
  const shouldShowShadow = scrollY > 20;

  /**
   * Xử lý đăng xuất
   */
  const handleLogout = async () => {
    try {
      // Gọi API đăng xuất trước
      await authApi.logout();
      // Sau đó xóa thông tin người dùng khỏi store
      dispatch(removeUser());
    } catch (error) {
      console.error("Lỗi khi đăng xuất:", error);
    }
  };

  /**
   * Hiển thị tên người dùng viết tắt
   */
  const getInitials = () => {
    if (!user) return "?";
    console.log("user", user);
    return user.username?.charAt(0).toUpperCase();
  };

  return (
    <header
      style={{
        // Sử dụng style inline để có thể áp dụng giá trị động chính xác
        backdropFilter: scrollY > 10 ? `blur(${backdropBlur}px)` : "none",
        boxShadow: shouldShowShadow
          ? `0 4px 10px -2px rgba(0, 0, 0, ${shadowOpacity})`
          : "none",
      }}
      className={`w-full py-4 sticky top-0 z-50 transition-all duration-500 bg-background/95 border-b theme-transition ${
        scrollY > 10
      }`}>
      <div className="container mx-auto flex items-center justify-between px-4">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-3 transition-all duration-300 hover:scale-105 transform hover:-rotate-1">
          <div className="relative h-10 w-10 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center font-bold shadow-md hover:shadow-lg theme-transition">
            <span className="text-lg font-bold">A</span>
            <span
              className={`absolute -top-1 -right-1 w-3 h-3 bg-accent rounded-full border-2  animate-pulse-slow theme-transition`}></span>
          </div>
          <span className="font-bold text-xl theme-transition">{appName}</span>
        </Link>

        {/* Menu chính - Desktop */}
        <nav className="hidden md:block">
          <ul className="flex items-center gap-8">
            <NavItem href="/" label="Trang chủ" isActive={pathname === "/"} />
            {user ? (
              <CoursesDropdown
                isActive={
                  pathname === "/courses" || pathname.startsWith("/courses/")
                }
              />
            ) : (
              <NavItem
                href="/courses/explore"
                label="Khóa học"
                isActive={
                  pathname === "/courses" || pathname.startsWith("/courses/")
                }
              />
            )}
            {/* <NavItem
              href="/learn"
              label="Bài học"
              isActive={pathname === "/learn" || pathname.startsWith("/learn/")}
            /> */}
            {/* <NavItem
              href="/exercises"
              label="Bài tập"
              isActive={
                pathname === "/exercises" || pathname.startsWith("/exercises/")
              }
            /> */}
            {user && (
              <NavItem
                href="/tests"
                label="Kiểm tra"
                isActive={
                  pathname === "/tests" || pathname.startsWith("/tests/")
                }
              />
            )}
            {user && (
              <NavItem
                href="/discussions"
                label="Thảo luận"
                isActive={
                  pathname === "/discussions" ||
                  pathname.startsWith("/discussions/")
                }
              />
            )}
            <NavItem
              href="/contact"
              label="Liên hệ"
              isActive={pathname === "/contact"}
            />
            <NavItem
              href="/about"
              label="FAQ"
              isActive={pathname === "/about"}
            />
            {user?.isAdmin && (
              <NavItem
                href="/admin"
                label="Quản trị"
                isActive={
                  pathname === "/admin" || pathname.startsWith("/admin/")
                }
              />
            )}
          </ul>
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-3">
          <div className="hidden md:flex items-center gap-3">
            {/* WebSocket Status */}
            <WebSocketStatus showText={false} className="mr-2" />

            {/* Theme Toggle */}
            <ThemeToggle />

            {user ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  className="flex items-center justify-center h-10 w-10 rounded-full bg-gradient-to-br from-primary to-secondary text-white font-medium shadow-sm hover:shadow transition-all transform hover:-translate-y-0.5"
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  aria-label="Menu người dùng">
                  {getInitials()}
                </button>

                {/* Dropdown menu */}
                {isUserMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-background border border-foreground/10 rounded-lg shadow-lg overflow-hidden z-50 theme-transition">
                    <div className="px-4 py-4 border-b border-foreground/10">
                      <p className="text-sm font-medium text-foreground">
                        {user?.username}
                      </p>
                      <p className="text-xs text-foreground/60 truncate">
                        {user?.email}
                      </p>
                    </div>
                    <Link
                      href="/profile"
                      className="block px-4 py-2 text-sm text-foreground hover:bg-foreground/10 transition-colors"
                      onClick={() => setIsUserMenuOpen(false)}>
                      Hồ sơ
                    </Link>
                    <Link
                      href="/settings"
                      className="block px-4 py-2 text-sm text-foreground hover:bg-foreground/10 transition-colors"
                      onClick={() => setIsUserMenuOpen(false)}>
                      Cài đặt
                    </Link>
                    <div
                      onClick={() => {
                        setIsUserMenuOpen(false);
                        handleLogout();
                      }}
                      className="w-full flex text-left px-4 py-2 text-sm text-red-500 hover:bg-foreground/10 transition-colors">
                      Đăng xuất
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className="px-4 py-2 text-sm font-medium rounded-lg hover:bg-foreground/10 transition-colors text-foreground theme-transition">
                  Đăng nhập
                </Link>
                <Link
                  href="/auth/register"
                  className="px-5 py-2 text-sm font-medium bg-primary text-white rounded-lg transition-all shadow-sm hover:shadow transform hover:-translate-y-0.5 theme-transition">
                  Đăng ký
                </Link>
              </>
            )}
          </div>

          {/* Menu Toggle - Mobile */}
          <button
            className="md:hidden items-center justify-center w-10 h-10 rounded-full hover:bg-foreground/10 transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label={isMenuOpen ? "Đóng menu" : "Mở menu"}>
            {isMenuOpen ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-foreground">
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-foreground">
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Menu Mobile */}
      {isMenuOpen && (
        <div
          className={`md:hidden bg-background py-4 px-4 border-t border-primary/10 animate-fade-in theme-transition`}>
          <nav className="flex flex-col gap-2">
            <MobileNavItem
              href="/"
              label="Trang chủ"
              isActive={pathname === "/"}
              onClick={() => setIsMenuOpen(false)}
            />
            {user && (
              <MobileNavItem
                href="/courses"
                label="Khóa học của bạn"
                isActive={pathname === "/courses"}
                onClick={() => setIsMenuOpen(false)}
              />
            )}
            {user && (
              <MobileNavItem
                href="/tests"
                label="Kiểm tra"
                isActive={
                  pathname === "/tests" || pathname.startsWith("/tests/")
                }
                onClick={() => setIsMenuOpen(false)}
              />
            )}
            <MobileNavItem
              href="/courses/explore"
              label="Khám phá khóa học"
              isActive={pathname === "/courses/explore"}
              onClick={() => setIsMenuOpen(false)}
            />
            {/* <MobileNavItem
              href="/exercises"
              label="Bài tập"
              isActive={
                pathname === "/exercises" || pathname.startsWith("/exercises/")
              }
              onClick={() => setIsMenuOpen(false)}
            /> */}
            {user && (
              <MobileNavItem
                href="/discussions"
                label="Thảo luận"
                isActive={
                  pathname === "/discussions" ||
                  pathname.startsWith("/discussions/")
                }
                onClick={() => setIsMenuOpen(false)}
              />
            )}
            <MobileNavItem
              href="/contact"
              label="Liên hệ"
              isActive={pathname === "/contact"}
              onClick={() => setIsMenuOpen(false)}
            />
            <MobileNavItem
              href="/about"
              label="FAQ"
              isActive={pathname === "/about"}
              onClick={() => setIsMenuOpen(false)}
            />
            {user?.isAdmin && (
              <MobileNavItem
                href="/admin"
                label="Quản trị"
                isActive={
                  pathname === "/admin" || pathname.startsWith("/admin/")
                }
                onClick={() => setIsMenuOpen(false)}
              />
            )}
          </nav>

          <div className="mt-5 flex flex-col gap-3">
            {/* Theme Toggle Mobile */}
            <div className="flex items-center justify-center mt-1 mb-3">
              <ThemeToggle />
            </div>

            {user ? (
              <>
                {/* User info - Mobile */}
                <div className="flex items-center gap-3 p-3 bg-foreground/5 rounded-lg mb-2">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-secondary text-white font-medium flex items-center justify-center">
                    {getInitials()}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground">
                      {user?.username}
                    </p>
                    <p className="text-xs text-foreground/60 truncate max-w-[200px]">
                      {user?.email}
                    </p>
                  </div>
                </div>
                <Link
                  href="/profile"
                  className={`w-full py-2.5 px-3 text-left text-sm font-medium border rounded-lg hover:bg-foreground/10 transition-colors theme-transition`}
                  onClick={() => setIsMenuOpen(false)}>
                  Hồ sơ của tôi
                </Link>
                <Link
                  href="/settings"
                  className={`w-full py-2.5 px-3 text-left text-sm font-medium border rounded-lg hover:bg-foreground/10 transition-colors theme-transition`}
                  onClick={() => setIsMenuOpen(false)}>
                  Cài đặt
                </Link>
                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    handleLogout();
                  }}
                  className="w-full py-2.5 text-left px-3 text-sm font-medium border border-red-200 text-red-500 hover:bg-red-50/30 rounded-lg transition-colors">
                  Đăng xuất
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/auth/login"
                  className={`w-full py-2.5 text-center text-sm font-medium border rounded-lg hover:bg-foreground/10 transition-colors theme-transition`}
                  onClick={() => setIsMenuOpen(false)}>
                  Đăng nhập
                </Link>
                <Link
                  href="/auth/register"
                  className="w-full py-2.5 text-center text-sm font-medium bg-gradient-to-r from-primary to-secondary hover:from-primary/90 hover:to-secondary/90 rounded-lg transition-colors shadow-sm hover:shadow text-white"
                  onClick={() => setIsMenuOpen(false)}>
                  Đăng ký
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

/**
 * Item menu cho desktop
 * @param {Object} props - Props của component
 * @param {string} props.href - Đường dẫn
 * @param {string} props.label - Nhãn hiển thị
 * @param {boolean} props.isActive - Trạng thái đang active
 */
function NavItem({
  href,
  label,
  isActive,
}: {
  href: string;
  label: string;
  isActive: boolean;
}) {
  return (
    <li className="relative group">
      <Link
        href={href}
        aria-current={isActive ? "page" : undefined}
        className={`relative px-1 py-2 font-medium theme-transition flex items-center ${
          isActive ? "text-primary" : "text-foreground/80 hover:text-primary"
        } transition-colors`}>
        {label}

        {/* Indicator thanh dưới chân - active */}
        {isActive && (
          <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-primary rounded-full animate-fade-in theme-transition"></span>
        )}

        {/* Indicator thanh dưới chân - hover */}
        {!isActive && (
          <span className="absolute -bottom-1 left-1/2 right-1/2 h-0.5 bg-[rgb(var(--color-primary))] rounded-full transition-all duration-300 group-hover:left-0 group-hover:right-0 theme-transition"></span>
        )}

        {/* Hiệu ứng glow khi hover */}
        <span className="absolute inset-0 rounded-md -z-10 opacity-0 group-hover:opacity-10 bg-primary blur-md transition-opacity duration-300"></span>
      </Link>
    </li>
  );
}

/**
 * Item menu cho mobile
 * @param {Object} props - Props của component
 * @param {string} props.href - Đường dẫn
 * @param {string} props.label - Nhãn hiển thị
 * @param {boolean} props.isActive - Trạng thái đang active
 * @param {() => void} props.onClick - Hàm xử lý khi click
 */
function MobileNavItem({
  href,
  label,
  isActive,
  onClick,
}: {
  href: string;
  label: string;
  isActive: boolean;
  onClick: () => void;
}) {
  return (
    <Link
      href={href}
      aria-current={isActive ? "page" : undefined}
      className={`relative px-4 py-2.5 rounded-lg theme-transition overflow-hidden group ${
        isActive
          ? "text-primary font-medium"
          : "text-foreground/80 hover:bg-foreground/10 hover:text-primary"
      } transition-all duration-300 hover:pl-6`}
      onClick={onClick}>
      {/* Thanh indicator bên trái */}
      <span className="absolute left-0 top-0 bottom-0 w-0 bg-primary/20 transition-all duration-300 group-hover:w-1"></span>

      {/* Indicator thanh dưới chân */}
      <span className="absolute bottom-0 left-4 right-4 h-0 bg-primary/20 rounded-t-md transition-all duration-300 group-hover:h-0.5"></span>

      {label}

      {/* Hiệu ứng đổ bóng nhẹ */}
      {isActive && (
        <span className="absolute inset-0 bg-primary/5 -z-10 rounded-md"></span>
      )}
    </Link>
  );
}

/**
 * Dropdown menu cho khóa học
 */
function CoursesDropdown({ isActive }: { isActive: boolean }) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLLIElement>(null);
  const pathname = usePathname();

  // Xử lý close dropdown khi click bên ngoài
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <li className="relative group" ref={dropdownRef}>
      <div
        className={`relative d-flex px-1 py-2 font-medium theme-transition flex items-center gap-1 ${
          isActive ? "text-primary" : "text-foreground/80 hover:text-primary"
        } transition-colors`}
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}>
        Khóa học
        <svg
          className={`w-4 h-4 transition-transform duration-200 ${
            isOpen ? "rotate-180" : ""
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
        {/* Indicator thanh dưới chân - active */}
        {isActive && (
          <span className="absolute -bottom-1 left-0 w-full h-0.5 bg-primary rounded-full animate-fade-in theme-transition"></span>
        )}
        {/* Indicator thanh dưới chân - hover */}
        {!isActive && (
          <span className="absolute -bottom-1 left-1/2 right-1/2 h-0.5 bg-[rgb(var(--color-primary))] rounded-full transition-all duration-300 group-hover:left-0 group-hover:right-0 theme-transition"></span>
        )}
      </div>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          className="absolute top-full left-0 mt-2 w-48 bg-background border border-border rounded-lg shadow-lg z-50 theme-transition"
          onMouseLeave={() => setIsOpen(false)}>
          <div className="py-2">
            <Link
              href="/courses"
              className={`block px-4 py-2 text-sm theme-transition ${
                pathname === "/courses"
                  ? "text-primary bg-primary/10"
                  : "text-foreground/80 hover:text-primary hover:bg-primary/5"
              }`}
              onClick={() => setIsOpen(false)}>
              Khóa học của bạn
            </Link>
            <Link
              href="/courses/explore"
              className={`block px-4 py-2 text-sm theme-transition ${
                pathname === "/courses/explore"
                  ? "text-primary bg-primary/10"
                  : "text-foreground/80 hover:text-primary hover:bg-primary/5"
              }`}
              onClick={() => setIsOpen(false)}>
              Khám phá khóa học
            </Link>
          </div>
        </div>
      )}
    </li>
  );
}
