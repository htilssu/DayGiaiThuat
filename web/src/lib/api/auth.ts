/**
 * Module chứa các API liên quan đến xác thực người dùng
 * @module api/auth
 */

import { get, post } from "./client";
import { ProfileData } from "@/services/profile.service";

/**
 * Interface cho dữ liệu đăng ký
 */
export interface RegisterData {
  email: string;
  password: string;
  fullName?: string;
}

/**
 * Interface cho phản hồi token
 */
export interface TokenResponse {
  accessToken: string;
  tokenType: string;
}

/**
 * Interface cho dữ liệu người dùng
 */
export interface UserData {
  id: number;
  email: string;
  username: string;
}

/**
 * Module API cho authentication
 */
const authApi = {
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
  ): Promise<TokenResponse> => {
    return post<TokenResponse>("/auth/login", {
      username,
      password,
      rememberMe,
    });
  },

  /**
   * Đăng ký tài khoản mới
   * @param userData - Thông tin người dùng đăng ký
   * @returns Promise chứa thông tin token
   */
  register: (userData: RegisterData): Promise<TokenResponse> => {
    return post<TokenResponse>("/auth/register", userData);
  },

  /**
   * Lấy thông tin người dùng hiện tại
   * @returns Promise chứa thông tin người dùng
   */
  getProfile: (): Promise<ProfileData> => {
    return get<ProfileData>("/users/me");
  },

  /**
   * Đăng xuất người dùng
   * @returns Promise chứa thông báo đăng xuất thành công
   */
  logout: (): Promise<{ message: string }> => {
    return post<{ message: string }>("/auth/logout");
  },
};

export default authApi;
