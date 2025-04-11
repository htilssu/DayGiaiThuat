"use client";

import { useTheme } from "@/contexts/ThemeContext";

/**
 * Component chuyển đổi theme
 *
 * @returns {React.ReactNode} Component chuyển đổi theme
 */
export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  // Xử lý khi click vào nút chuyển đổi theme
  const handleToggle = () => {
    // Chuyển đổi qua lại giữa light và dark
    setTheme(theme === "dark" ? "light" : "dark");
  };

  // Biểu tượng cho light mode (mặt trời)
  const SunIcon = () => (
    <svg
      className="w-5 h-5 text-yellow-400"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
      />
    </svg>
  );

  // Biểu tượng cho dark mode (mặt trăng)
  const MoonIcon = () => (
    <svg
      className="w-5 h-5 text-primary/90"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
      />
    </svg>
  );

  return (
    <button
      onClick={handleToggle}
      className={`p-2 rounded-full hover:bg-foreground/10 transition-colors ${
        theme === "dark"
          ? "bg-slate-800/50 hover:bg-slate-700/50"
          : "bg-gray-100/80 hover:bg-gray-200/80"
      }`}
      aria-label={
        theme === "dark" ? "Chuyển sang chế độ sáng" : "Chuyển sang chế độ tối"
      }
    >
      {theme === "dark" ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}
