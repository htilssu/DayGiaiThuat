"use client";

import { setTheme } from "@/lib/utils/theme";

import { getTheme } from "@/lib/utils/theme";
import { useState } from "react";

/**
 * Component chuyển đổi theme
 *
 * @returns {React.ReactNode} Component chuyển đổi theme
 */
export default function ThemeToggle() {
  // Xử lý khi click vào nút chuyển đổi theme
  const [currentTheme, setCurrentTheme] = useState(getTheme());

  const handleToggle = () => {
    const newTheme = currentTheme === "light" ? "dark" : "light";
    setTheme(newTheme);
    setCurrentTheme(newTheme);
  };

  // Biểu tượng cho light mode (mặt trời)
  const SunIcon = () => (
    <svg
      className="w-5 h-5 text-[rgb(var(--color-primary))]"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
      />
    </svg>
  );

  // Biểu tượng cho dark mode (mặt trăng)
  const ChangeThemeButton = () => (
    <svg
      className="w-5 h-5 text-[rgb(var(--color-secondary))]"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor">
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
      />
    </svg>
  );
  if (currentTheme !== "dark") {
    return (
      <button
        onClick={handleToggle}
        className={`p-2 rounded-full hover:bg-primary/10 transition-colors`}
        aria-label="Chuyển đổi theme">
      </button>
    );
  }
  return (
    <button
      key={currentTheme}
      onClick={handleToggle}
      className={`p-2 rounded-full hover:bg-primary/10 transition-colors`}
      aria-label="Chuyển đổi theme">
      <SunIcon />
    </button>
  );
}
