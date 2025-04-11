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
 * @property {boolean} isLoaded - Trạng thái đã load xong theme từ localStorage
 */
interface ThemeContextType {
  theme: ThemeType;
  toggleTheme: () => void;
  setTheme: (theme: ThemeType) => void;
  isLoaded: boolean;
}

/**
 * Context quản lý theme toàn cục
 */
const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

/**
 * Hàm lưu theme vào localStorage
 * @param {ThemeType} theme - Theme cần lưu
 */
const saveThemeToStorage = (theme: ThemeType): void => {
  try {
    if (typeof window !== "undefined") {
      localStorage.setItem("theme", theme);
    }
  } catch (error) {
    console.error("Không thể lưu theme vào localStorage:", error);
  }
};

/**
 * Hàm đọc theme từ localStorage
 * @returns {ThemeType | null} Theme đã lưu hoặc null nếu không tìm thấy
 */
const getThemeFromStorage = (): ThemeType | null => {
  try {
    if (typeof window !== "undefined") {
      return localStorage.getItem("theme") as ThemeType | null;
    }
    return null;
  } catch (error) {
    console.error("Không thể đọc theme từ localStorage:", error);
    return null;
  }
};

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
  const [theme, setThemeState] = useState<ThemeType>("light");
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  // Wrapper để cập nhật state và lưu vào localStorage
  const setTheme = (newTheme: ThemeType) => {
    setThemeState(newTheme);
    saveThemeToStorage(newTheme);
  };

  // Hàm chuyển đổi giữa light và dark
  const toggleTheme = () => {
    setTheme(theme === "light" ? "dark" : "light");
  };

  // Cập nhật theme trong DOM
  useEffect(() => {
    // Cập nhật data-theme attribute trên document
    if (typeof document !== "undefined") {
      const root = document.documentElement;
      root.setAttribute("data-theme", theme);
      root.dataset.theme = theme;
    }
  }, [theme]);

  // Khôi phục theme từ localStorage hoặc dùng theme hệ thống khi khởi tạo
  useEffect(() => {
    if (typeof window === "undefined") return;

    // Xử lý trên client-side
    const initializeTheme = () => {
      // Lấy theme từ localStorage
      const savedTheme = getThemeFromStorage();

      if (savedTheme) {
        // Nếu đã lưu theme trước đó, dùng lại
        setThemeState(savedTheme);
      } else {
        // Nếu chưa lưu, kiểm tra theme hệ thống
        const prefersDark = window.matchMedia(
          "(prefers-color-scheme: dark)"
        ).matches;
        const systemTheme = prefersDark ? "dark" : "light";
        setThemeState(systemTheme);
        saveThemeToStorage(systemTheme);
      }

      setIsLoaded(true);
    };

    initializeTheme();

    // Lắng nghe sự thay đổi theme hệ thống
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      const newTheme = e.matches ? "dark" : "light";
      // Chỉ cập nhật theo hệ thống nếu chưa có lưu trước đó
      if (!getThemeFromStorage()) {
        setTheme(newTheme);
      }
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme, isLoaded }}>
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
