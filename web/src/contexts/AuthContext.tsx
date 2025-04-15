"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { useRouter } from "next/navigation";

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
  login: (token: string) => void;
  logout: () => void;
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
      const token =
        localStorage.getItem("token") || sessionStorage.getItem("token");

      if (token) {
        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            // Nếu token không hợp lệ, xóa token và chuyển về trang login
            localStorage.removeItem("token");
            sessionStorage.removeItem("token");
            router.push("/auth/login");
          }
        } catch (error) {
          console.error("Lỗi khi kiểm tra xác thực:", error);
        }
      }

      setIsLoading(false);
    };

    checkAuth();
  }, [router]);

  /**
   * Hàm xử lý đăng nhập
   * @param token - JWT token nhận được từ server
   */
  const login = async (token: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error("Lỗi khi lấy thông tin user:", error);
    }
  };

  /**
   * Hàm xử lý đăng xuất
   */
  const logout = () => {
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
