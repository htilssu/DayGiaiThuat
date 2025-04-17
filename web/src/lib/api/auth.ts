/**
 * Module chứa các API liên quan đến xác thực người dùng
 * @module api/auth
 */

import { get, post } from "./client";

/**
 * Interface cho dữ liệu đăng ký
 */
export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

/**
 * Interface cho phản hồi token
 */
export interface TokenResponse {
  access_token: string;
  token_type: string;
}

/**
 * Interface cho dữ liệu người dùng
 */
export interface UserData {
  id: string;
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
  login: (email: string, password: string): Promise<TokenResponse> => {
    const formData = new FormData();
    formData.append("username", email);
    formData.append("password", password);

    return post<TokenResponse>("/auth/login", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });
  },

  /**
   * Đăng ký tài khoản mới
   * @param userData - Thông tin người dùng đăng ký
   * @returns Promise chứa thông tin người dùng đã đăng ký
   */
  register: (userData: RegisterData): Promise<UserData> => {
    return post<UserData>("/auth/register", userData);
  },

  /**
   * Lấy thông tin người dùng hiện tại
   * @returns Promise chứa thông tin người dùng
   */
  getProfile: (): Promise<UserData> => {
    return get<UserData>("/users/me");
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
