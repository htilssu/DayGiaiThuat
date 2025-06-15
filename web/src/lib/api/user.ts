/**
 * Module chứa các API liên quan đến quản lý người dùng
 * @module api/user
 */

import { UserData } from "./auth";
import { get, post, put, del } from "./client";

/**
 * Interface cho dữ liệu cập nhật hồ sơ người dùng
 */
export interface UpdateProfileData {
  fullName?: string;
  avatar?: string;
  bio?: string;
}

/**
 * Interface cho phản hồi danh sách người dùng
 */
export interface UsersListResponse {
  items: UserData[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
}

/**
 * Module API cho quản lý người dùng
 */
export const userApi = {
  /**
   * Lấy danh sách người dùng
   * @param page - Số trang
   * @param perPage - Số lượng bản ghi mỗi trang
   * @returns Promise chứa danh sách người dùng
   */
  getUsers: (
    page: number = 1,
    perPage: number = 10
  ): Promise<UsersListResponse> => {
    return get<UsersListResponse>(`/users?page=${page}&per_page=${perPage}`);
  },

  /**
   * Lấy thông tin người dùng theo ID
   * @param userId - ID của người dùng
   * @returns Promise chứa thông tin người dùng
   */
  getUserById: (userId: string): Promise<UserData> => {
    return get<UserData>(`/users/${userId}`);
  },

  /**
   * Cập nhật thông tin hồ sơ người dùng
   * @param profileData - Dữ liệu cập nhật hồ sơ
   * @returns Promise chứa thông tin người dùng đã cập nhật
   */
  updateProfile: (profileData: UpdateProfileData): Promise<UserData> => {
    // Chuyển đổi tên trường để phù hợp với API
    const apiData = {
      fullName: profileData.fullName,
      avatarUrl: profileData.avatar,
      bio: profileData.bio,
    };

    return put<UserData>("/users/me", apiData);
  },

  /**
   * Thay đổi mật khẩu người dùng
   * @param currentPassword - Mật khẩu hiện tại
   * @param newPassword - Mật khẩu mới
   * @returns Promise chứa thông báo thành công
   */
  changePassword: (
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> => {
    return post<{ message: string }>("/users/me/change-password", {
      currentPassword,
      newPassword,
    });
  },

  /**
   * Xóa tài khoản người dùng
   * @returns Promise chứa thông báo thành công
   */
  deleteAccount: (): Promise<{ message: string }> => {
    return del<{ message: string }>("/users/me");
  },
  getUserByToken: () => {
    return get<UserData>("/user");
  }
};
