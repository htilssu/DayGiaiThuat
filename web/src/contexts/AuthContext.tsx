"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import api from "@/lib/api";
import {
  ProfileData,
  transformUserData,
  AppError,
  ErrorType,
  TransformedUserData,
} from "@/services/profile.service";
import { publicPaths } from "@/middleware";

/**
 * Interface định nghĩa context xác thực
 */
interface AuthContextType {
  user: TransformedUserData | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (token?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUserInfo: (userData: Partial<TransformedUserData>) => void;
  clearError: () => void;
}

/**
 * Context xác thực được tạo với giá trị mặc định là null
 */
const AuthContext = createContext<AuthContextType | null>(null);

/**
 * Props cho AuthProvider component
 */
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * AuthProvider component cung cấp context xác thực cho toàn bộ ứng dụng
 * @param children - Các component con
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<TransformedUserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const pathname = usePathname();

  /**
   * Hàm xóa thông báo lỗi
   */
  const clearError = () => {
    setError(null);
  };

  /**
   * Kiểm tra nếu đường dẫn hiện tại là đường dẫn công khai
   * @param {string} path - Đường dẫn cần kiểm tra
   * @returns {boolean} - true nếu đường dẫn là công khai
   */
  const isPublicPath = (path: string): boolean => {
    return publicPaths.some((publicPath) => path.startsWith(publicPath));
  };

  /**
   * Hàm xử lý khi token hết hạn hoặc không hợp lệ
   * @param redirectUrl - Đường dẫn chuyển hướng sau khi xử lý
   */
  const handleAuthError = (redirectUrl: string = "/auth/login") => {
    setUser(null);

    // Chỉ chuyển hướng nếu không phải là đường dẫn công khai
    if (!isPublicPath(pathname || "")) {
      // Thêm đường dẫn hiện tại vào returnUrl
      const loginUrl = `${redirectUrl}?returnUrl=${encodeURIComponent(
        pathname || "/"
      )}`;
      router.push(loginUrl);
    }
  };

  useEffect(() => {
    const checkAuth = async () => {
      try {
        setIsLoading(true);
        // Lấy thông tin người dùng từ API
        const apiUserData = (await api.auth.getProfile()) as ProfileData;

        // Chuyển đổi dữ liệu để phù hợp với cấu trúc frontend
        const userData = transformUserData(apiUserData);

        setUser(userData);
        clearError();
      } catch (error: any) {
        console.error("Lỗi khi kiểm tra xác thực:", error);

        let errorMessage = "Lỗi xác thực không xác định";

        if (error instanceof AppError) {
          errorMessage = error.message;

          // Xử lý lỗi xác thực
          if (error.type === ErrorType.AUTHENTICATION_ERROR) {
            handleAuthError();
          }
        } else {
          // Xử lý lỗi khác
          handleAuthError();
        }

        setError(errorMessage);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  /**
   * Hàm xử lý đăng nhập
   * @param token - JWT token không còn được sử dụng trực tiếp (giữ lại để tương thích ngược)
   */
  const login = async (token?: string) => {
    try {
      setIsLoading(true);

      // Lấy thông tin người dùng từ API
      const apiUserData = (await api.auth.getProfile()) as ProfileData;

      // Chuyển đổi dữ liệu để phù hợp với cấu trúc frontend
      const userData = transformUserData(apiUserData);

      setUser(userData);
      clearError();
    } catch (error: any) {
      console.error("Lỗi khi lấy thông tin user:", error);

      let errorMessage = "Lỗi đăng nhập không xác định";

      if (error instanceof AppError) {
        errorMessage = error.message;
      }

      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Cập nhật thông tin người dùng
   * @param userData - Thông tin người dùng cần cập nhật
   */
  const updateUserInfo = (userData: Partial<TransformedUserData>) => {
    if (user) {
      setUser({ ...user, ...userData });
    }
  };

  /**
   * Hàm xử lý đăng xuất
   */
  const logout = async () => {
    try {
      setIsLoading(true);
      // Gọi API đăng xuất để xóa cookie phía server
      await api.auth.logout();
    } catch (error: any) {
      console.error("Lỗi khi đăng xuất:", error);

      let errorMessage = "Lỗi khi đăng xuất";

      if (error instanceof AppError) {
        errorMessage = error.message;
      }

      setError(errorMessage);
    } finally {
      // Dù API có lỗi hay không, vẫn xóa dữ liệu người dùng ở client
      setUser(null);
      // Chuyển hướng đến trang đăng nhập sau khi đăng xuất
      router.push("/auth/login");
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    logout,
    updateUserInfo,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook tùy chỉnh để sử dụng AuthContext
 * @returns AuthContextType
 * @throws Error nếu được sử dụng bên ngoài AuthProvider
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth phải được sử dụng trong AuthProvider");
  }
  return context;
}
