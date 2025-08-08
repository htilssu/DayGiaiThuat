import { post } from "./client";

/**
 * Interface cho dữ liệu đăng ký
 */
export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

/**
 * Interface cho phản hồi token
 */
export interface LoginResponse {
  accessToken: string;
  tokenType: string;
  user: UserData;
}

/**
 * Interface cho dữ liệu người dùng
 */
export interface UserData {
  id: number;
  email: string;
  username: string;
  avatar: string;
  fullName: string;
  isAdmin?: boolean;
  isActive?: boolean;
}

/**
 * Module API cho authentication
 */
export const authApi = {
  /**
   * Đăng nhập người dùng
   * @param email - Email người dùng
   * @param password - Mật khẩu người dùng
   * @returns Promise chứa thông tin token
   */
  login: (
    username: string,
    password: string,
    rememberMe: boolean
  ): Promise<LoginResponse> => {
    return post<LoginResponse>("/auth/login", {
      username,
      password,
      rememberMe,
    });
  },

  register: (userData: RegisterData): Promise<LoginResponse> => {
    return post<LoginResponse>("/auth/register", userData);
  },

  /**
   * Đăng xuất người dùng
   * @returns Promise chứa thông báo đăng xuất thành công
   */
  logout: (): Promise<{ message: string }> => {
    return post<{ message: string }>("/auth/logout");
  },
};
