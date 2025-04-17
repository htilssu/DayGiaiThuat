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

/**
 * Interface định nghĩa dữ liệu người dùng
 */
interface User {
  id: string;
  email: string;
  username: string;
}

/**
 * Interface định nghĩa context xác thực
 */
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token?: string) => Promise<void>;
  logout: () => Promise<void>;
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
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Kiểm tra token và lấy thông tin user khi component được mount
  useEffect(() => {
    const checkAuth = async () => {
      // Kiểm tra xem người dùng đã đăng nhập chưa (cookie hoặc localStorage)
      if (isAuthenticated()) {
        try {
          console.log("Kiểm tra xác thực với token");

          // Sử dụng API util thay thế cho fetch trực tiếp
          const userData = (await api.auth.getProfile()) as User;
          setUser(userData);
        } catch (error: any) {
          console.error("Lỗi khi kiểm tra xác thực:", error);

          // Nếu token không hợp lệ, xóa token từ localStorage và chuyển về trang login
          localStorage.removeItem("token");
          sessionStorage.removeItem("token");
          router.push("/auth/login");
        }
      }

      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  /**
   * Hàm xử lý đăng nhập
   * @param token - JWT token nhận được từ server (tùy chọn vì sẽ dùng cookie)
   */
  const login = async (token?: string) => {
    try {
      // Lưu token vào localStorage nếu được cung cấp (tương thích ngược)
      if (token) {
        localStorage.setItem("token", token);
      }

      // Kiểm tra xem token có trong localStorage không
      const storedToken = localStorage.getItem("token");
      if (!storedToken && !getTokenFromCookie()) {
        throw new Error("Không tìm thấy token xác thực");
      }

      // Sử dụng API util thay thế cho fetch trực tiếp
      const userData = (await api.auth.getProfile()) as User;
      setUser(userData);
    } catch (error) {
      console.error("Lỗi khi lấy thông tin user:", error);
      throw error;
    }
  };

  /**
   * Hàm xử lý đăng xuất
   */
  const logout = async () => {
    try {
      // Gọi API đăng xuất để xóa cookie phía server
      await api.auth.logout();
    } catch (error) {
      console.error("Lỗi khi đăng xuất:", error);
    }

    // Dù API có lỗi hay không, vẫn xóa dữ liệu người dùng và token ở client
    setUser(null);
    localStorage.removeItem("token");
    sessionStorage.removeItem("token");
    router.push("/auth/login");
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
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
