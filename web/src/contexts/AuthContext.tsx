"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import api, { getTokenFromCookie, isAuthenticated } from "@/lib/api";
import {
  ProfileData,
  transformUserData,
  AppError,
  ErrorType,
} from "@/services/profile.service";

/**
 * Interface định nghĩa context xác thực
 */
interface AuthContextType {
  user: any | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (token?: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUserInfo: (userData: Partial<any>) => void;
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
  const [user, setUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  /**
   * Hàm xóa thông báo lỗi
   */
  const clearError = () => {
    setError(null);
  };

  // Kiểm tra token và lấy thông tin user khi component được mount
  useEffect(() => {
    const checkAuth = async () => {
      // Kiểm tra xem người dùng đã đăng nhập chưa (thông qua cookie)
      if (isAuthenticated()) {
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

            // Nếu lỗi xác thực, đưa người dùng về trang đăng nhập
            if (error.type === ErrorType.AUTHENTICATION_ERROR) {
              router.push("/auth/login");
            }
          } else {
            // Nếu token không hợp lệ, đưa người dùng về trang login
            router.push("/auth/login");
          }

          setError(errorMessage);
          setUser(null);
        } finally {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router]);

  /**
   * Hàm xử lý đăng nhập
   * @param token - JWT token không còn được sử dụng trực tiếp (giữ lại để tương thích ngược)
   */
  const login = async (token?: string) => {
    try {
      setIsLoading(true);

      // Token được xử lý tự động thông qua cookie từ phản hồi của server
      // Nếu không có cookie token, đây là lỗi
      if (!getTokenFromCookie()) {
        throw new AppError(
          "Không tìm thấy token xác thực",
          ErrorType.AUTHENTICATION_ERROR
        );
      }

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
  const updateUserInfo = (userData: Partial<any>) => {
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
