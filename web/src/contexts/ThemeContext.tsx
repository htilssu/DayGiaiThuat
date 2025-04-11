"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

/**
 * Kiểu dữ liệu cho theme hệ thống
 * @typedef {'light' | 'dark'} ThemeType
 */
type ThemeType = "light" | "dark";

/**
 * Interface định nghĩa các giá trị và phương thức context theme cung cấp
 * @interface ThemeContextType
 * @property {ThemeType} theme - Theme hiện tại (light/dark)
 * @property {() => void} toggleTheme - Hàm chuyển đổi giữa các theme
 * @property {(theme: ThemeType) => void} setTheme - Hàm thiết lập theme cụ thể
 */
interface ThemeContextType {
  theme: ThemeType;
  toggleTheme: () => void;
  setTheme: (theme: ThemeType) => void;
}

/**
 * Context quản lý theme toàn cục
 */
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * Props cho ThemeProvider
 * @interface ThemeProviderProps
 * @property {ReactNode} children - Các component con
 */
interface ThemeProviderProps {
  children: ReactNode;
}

/**
 * Provider cho context theme, quản lý trạng thái theme và cung cấp các phương thức thay đổi
 * @param {ThemeProviderProps} props - Properties của component
 * @returns {ReactNode} - Provider component
 */
export function ThemeProvider({ children }: ThemeProviderProps): ReactNode {
  // Khởi tạo state theme với giá trị mặc định là 'light'
  const [theme, setTheme] = useState<ThemeType>("light");

  // Hàm chuyển đổi giữa light và dark
  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === "light" ? "dark" : "light"));
  };

  // Cập nhật theme trong DOM và lưu vào localStorage
  useEffect(() => {
    // Lưu theme vào localStorage
    localStorage.setItem("theme", theme);

    // Cập nhật data-theme attribute trên document
    const root = document.documentElement;
    root.setAttribute("data-theme", theme);

    // Dùng dataset cho tương thích tốt hơn
    document.documentElement.dataset.theme = theme;
  }, [theme]);

  // Khôi phục theme từ localStorage hoặc dùng theme hệ thống khi khởi tạo
  useEffect(() => {
    // Lấy theme từ localStorage
    const savedTheme = localStorage.getItem("theme") as ThemeType | null;

    if (savedTheme) {
      // Nếu đã lưu theme trước đó, dùng lại
      setTheme(savedTheme);
    } else {
      // Nếu chưa lưu, kiểm tra theme hệ thống
      const prefersDark = window.matchMedia(
        "(prefers-color-scheme: dark)"
      ).matches;
      setTheme(prefersDark ? "dark" : "light");

      // Lắng nghe sự thay đổi theme hệ thống
      const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
      const handleChange = (e: MediaQueryListEvent) => {
        setTheme(e.matches ? "dark" : "light");
      };

      mediaQuery.addEventListener("change", handleChange);
      return () => mediaQuery.removeEventListener("change", handleChange);
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook để sử dụng theme trong các component
 * @returns {ThemeContextType} Các giá trị và phương thức quản lý theme
 * @throws {Error} Lỗi nếu dùng hook bên ngoài ThemeProvider
 */
export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error("useTheme phải được sử dụng trong ThemeProvider");
  }

  return context;
}
