/**
 * Module chứa các API liên quan đến quản lý người dùng
 * @module api/user
 */

import { UserData } from "./auth";
import { get, post, put, patch, del } from "./client";

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
 * Interface cho tạo người dùng mới (Admin)
 */
export interface AdminUserCreate {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  is_admin?: boolean;
  is_active?: boolean;
  bio?: string;
  avatar_url?: string;
}

/**
 * Interface cho cập nhật người dùng (Admin)
 */
export interface AdminUserUpdate {
  email?: string;
  username?: string;
  first_name?: string;
  last_name?: string;
  is_admin?: boolean;
  is_active?: boolean;
  bio?: string;
  avatar_url?: string;
}

/**
 * Interface cho phản hồi người dùng (Admin)
 */
export interface AdminUserResponse {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  is_active: boolean;
  bio?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Interface cho bulk delete request
 */
export interface BulkDeleteUsersRequest {
  userIds: number[];
  force?: boolean;
}

/**
 * Interface cho bulk delete response
 */
export interface BulkDeleteUsersResponse {
  deletedCount: number;
  message: string;
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
    return get<UserData>("/users");
  },

  // ===== ADMIN USER MANAGEMENT APIs =====

  /**
   * Tạo người dùng mới (Admin)
   * @param userData - Dữ liệu người dùng mới
   * @returns Promise chứa thông tin người dùng đã tạo
   */
  createUserAdmin: (userData: AdminUserCreate): Promise<AdminUserResponse> => {
    return post<AdminUserResponse>("/users/admin", userData);
  },

  /**
   * Lấy danh sách tất cả người dùng (Admin)
   * @param skip - Số bản ghi bỏ qua
   * @param limit - Số lượng bản ghi tối đa
   * @returns Promise chứa danh sách người dùng
   */
  getAllUsersAdmin: (
    skip: number = 0,
    limit: number = 100
  ): Promise<AdminUserResponse[]> => {
    return get<AdminUserResponse[]>(`/users/admin?skip=${skip}&limit=${limit}`);
  },

  /**
   * Lấy thông tin người dùng theo ID (Admin)
   * @param userId - ID của người dùng
   * @returns Promise chứa thông tin người dùng
   */
  getUserByIdAdmin: (userId: number): Promise<AdminUserResponse> => {
    return get<AdminUserResponse>(`/users/admin/${userId}`);
  },

  /**
   * Cập nhật thông tin người dùng (Admin)
   * @param userId - ID của người dùng
   * @param userData - Dữ liệu cập nhật
   * @returns Promise chứa thông tin người dùng đã cập nhật
   */
  updateUserAdmin: (
    userId: number,
    userData: AdminUserUpdate
  ): Promise<AdminUserResponse> => {
    return put<AdminUserResponse>(`/users/admin/${userId}`, userData);
  },

  /**
   * Vô hiệu hóa người dùng (Admin)
   * @param userId - ID của người dùng
   * @returns Promise chứa thông tin người dùng đã vô hiệu hóa
   */
  deactivateUserAdmin: (userId: number): Promise<AdminUserResponse> => {
    return patch<AdminUserResponse>(`/users/admin/${userId}/deactivate`);
  },

  /**
   * Kích hoạt người dùng (Admin)
   * @param userId - ID của người dùng
   * @returns Promise chứa thông tin người dùng đã kích hoạt
   */
  activateUserAdmin: (userId: number): Promise<AdminUserResponse> => {
    return patch<AdminUserResponse>(`/users/admin/${userId}/activate`);
  },

  /**
   * Xóa người dùng (Admin)
   * @param userId - ID của người dùng
   * @param force - Bắt buộc xóa
   * @returns Promise chứa thông báo thành công
   */
  deleteUserAdmin: (
    userId: number,
    force: boolean = false
  ): Promise<{ message: string }> => {
    return del<{ message: string }>(`/users/admin/${userId}?force=${force}`);
  },

  /**
   * Xóa nhiều người dùng (Admin)
   * @param request - Dữ liệu xóa hàng loạt
   * @returns Promise chứa kết quả xóa hàng loạt
   */
  bulkDeleteUsersAdmin: (
    request: BulkDeleteUsersRequest
  ): Promise<BulkDeleteUsersResponse> => {
    return del<BulkDeleteUsersResponse>("/users/admin/bulk", request);
  },
};
