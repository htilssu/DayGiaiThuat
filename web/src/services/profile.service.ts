import api from "@/lib/api";
import { get, post, put } from "@/lib/api/client";

/**
 * Interface định nghĩa dữ liệu thống kê người dùng
 */
export interface UserStats {
  completed_exercises: number;
  completed_courses: number;
  total_points: number;
  streak_days: number;
  level: number;
  problems_solved: number;
}

/**
 * Interface định nghĩa dữ liệu huy hiệu
 */
export interface Badge {
  id: number;
  name: string;
  icon: string;
  description: string;
  unlocked: boolean;
}

/**
 * Interface định nghĩa dữ liệu tiến độ khóa học
 */
export interface CourseProgress {
  id: string;
  name: string;
  progress: number; // 0-100
  color_from: string;
  color_to: string;
  image_url?: string;
}

/**
 * Interface định nghĩa dữ liệu hoạt động gần đây
 */
export interface Activity {
  id: number;
  type: string;
  name: string;
  date: string;
  score?: string;
  progress?: string;
}

/**
 * Interface định nghĩa dữ liệu học tập
 */
export interface LearningProgress {
  algorithms: number;
  data_structures: number;
  dynamic_programming: number;
}

/**
 * Interface định nghĩa dữ liệu profile đầy đủ
 */
export interface ProfileData {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  bio?: string;
  avatar_url?: string;
  joinDate?: string;
  stats: UserStats;
  badges: Badge[];
  activities: Activity[];
  learning_progress: LearningProgress;
  courses: CourseProgress[];
}

/**
 * Interface đơn giản hóa cho dữ liệu từ AuthContext
 */
export interface AuthUserData {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  bio?: string;
  avatar_url?: string;
  created_at?: string;
  updated_at?: string;
  is_active: boolean;
  joinDate?: string;
  stats?: UserStats;
  badges?: Badge[];
  activities?: Activity[];
  learning_progress?: LearningProgress;
  courses?: CourseProgress[];
}

/**
 * Loại lỗi của hệ thống
 */
export enum ErrorType {
  NETWORK_ERROR = "NETWORK_ERROR",
  SERVER_ERROR = "SERVER_ERROR",
  AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR",
  NOT_FOUND = "NOT_FOUND",
  VALIDATION_ERROR = "VALIDATION_ERROR",
  UNKNOWN_ERROR = "UNKNOWN_ERROR",
}

/**
 * Lớp lỗi tùy chỉnh cho hệ thống
 */
export class AppError extends Error {
  type: ErrorType;
  statusCode?: number;

  constructor(message: string, type: ErrorType, statusCode?: number) {
    super(message);
    this.type = type;
    this.statusCode = statusCode;
    this.name = "AppError";
  }
}

/**
 * Chuyển đổi dữ liệu từ API sang dạng dữ liệu frontend thân thiện
 * @param userData Dữ liệu người dùng từ API
 * @returns ProfileData với tên trường đã được chuyển đổi
 */
export const transformUserData = (userData: ProfileData): any => {
  if (!userData) {
    throw new AppError(
      "Dữ liệu người dùng không hợp lệ",
      ErrorType.VALIDATION_ERROR
    );
  }

  // Đảm bảo dữ liệu có cấu trúc cần thiết
  if (!userData.stats || !userData.learning_progress) {
    throw new AppError(
      "Dữ liệu người dùng thiếu thông tin quan trọng",
      ErrorType.VALIDATION_ERROR
    );
  }

  return {
    id: userData.id,
    username: userData.username,
    email: userData.email,
    fullName: userData.full_name || userData.username,
    isActive: userData.is_active,
    createdAt: userData.created_at,
    updatedAt: userData.updated_at,
    bio: userData.bio || "",
    avatar: userData.avatar_url || "/placeholder-avatar.png",
    joinDate:
      userData.joinDate ||
      new Date(userData.created_at).toLocaleDateString("vi-VN"),
    stats: {
      completedExercises: userData.stats.completed_exercises,
      completedCourses: userData.stats.completed_courses,
      totalPoints: userData.stats.total_points,
      streak: userData.stats.streak_days,
      level: userData.stats.level,
      problemsSolved: userData.stats.problems_solved,
    },
    badges: userData.badges || [],
    activities: userData.activities || [],
    learningProgress: {
      algorithms: userData.learning_progress.algorithms,
      dataStructures: userData.learning_progress.data_structures,
      dynamicProgramming: userData.learning_progress.dynamic_programming,
    },
    courses: (userData.courses || []).map((course) => ({
      id: course.id,
      name: course.name,
      progress: course.progress,
      colorFrom: course.color_from,
      colorTo: course.color_to,
      imageUrl: course.image_url,
    })),
  };
};

/**
 * Tạo ProfileData cơ bản từ thông tin user trong AuthContext
 * @param userData Dữ liệu người dùng từ AuthContext
 * @returns ProfileData đã được chuyển đổi sang định dạng frontend
 * @throws AppError nếu dữ liệu không hợp lệ
 */
export const createBasicProfileFromAuth = (userData: AuthUserData): any => {
  if (!userData) {
    throw new AppError(
      "Dữ liệu người dùng không hợp lệ",
      ErrorType.VALIDATION_ERROR
    );
  }

  // Nếu userData đã có đầy đủ dữ liệu, chuyển đổi nó
  if (userData.stats && userData.learning_progress && userData.courses) {
    return transformUserData(userData as unknown as ProfileData);
  }

  // Không còn dùng dữ liệu mẫu, thay vào đó ném lỗi
  throw new AppError(
    "Dữ liệu người dùng không đầy đủ, vui lòng làm mới trang",
    ErrorType.VALIDATION_ERROR
  );
};

/**
 * Service quản lý dữ liệu profile người dùng
 */
const profileService = {
  /**
   * Lấy dữ liệu profile người dùng
   * @param userId - ID của người dùng (không bắt buộc, mặc định lấy profile hiện tại)
   * @returns Promise chứa dữ liệu profile đã được chuyển đổi
   * @throws AppError nếu có lỗi khi lấy dữ liệu
   */
  getProfile: async (userId?: number): Promise<any> => {
    try {
      // Nếu có userId, gọi API để lấy thông tin người dùng cụ thể
      // Nếu không, lấy thông tin người dùng hiện tại
      const endpoint = userId ? `/users/${userId}` : "/users/me";
      const profileData = await get<ProfileData>(endpoint);

      if (!profileData) {
        throw new AppError(
          "Không thể lấy thông tin người dùng",
          ErrorType.NOT_FOUND
        );
      }

      return transformUserData(profileData);
    } catch (error: any) {
      console.error("Lỗi khi lấy dữ liệu profile:", error);

      // Phân loại lỗi để xử lý phù hợp
      if (error instanceof AppError) {
        throw error;
      }

      // Xử lý lỗi từ API và chuyển đổi thành lỗi ứng dụng
      if (error.status === 401 || error.status === 403) {
        throw new AppError(
          "Không có quyền truy cập thông tin người dùng",
          ErrorType.AUTHENTICATION_ERROR,
          error.status
        );
      } else if (error.status === 404) {
        throw new AppError(
          "Không tìm thấy thông tin người dùng",
          ErrorType.NOT_FOUND,
          error.status
        );
      } else if (error.status >= 500) {
        throw new AppError(
          "Lỗi máy chủ khi lấy thông tin người dùng",
          ErrorType.SERVER_ERROR,
          error.status
        );
      } else {
        throw new AppError(
          "Lỗi không xác định khi lấy thông tin người dùng",
          ErrorType.UNKNOWN_ERROR
        );
      }
    }
  },

  /**
   * Cập nhật thông tin profile người dùng
   * @param profileData Dữ liệu cập nhật
   * @returns Promise chứa thông tin đã cập nhật
   * @throws AppError nếu có lỗi khi cập nhật
   */
  updateProfile: async (profileData: {
    fullName?: string;
    bio?: string;
    avatar?: string;
  }): Promise<any> => {
    try {
      if (!profileData) {
        throw new AppError(
          "Dữ liệu cập nhật không hợp lệ",
          ErrorType.VALIDATION_ERROR
        );
      }

      // Chuyển đổi tên trường để phù hợp với API
      const apiData = {
        full_name: profileData.fullName,
        bio: profileData.bio,
        avatar_url: profileData.avatar,
      };

      const updatedUser = await put<ProfileData>("/users/me", apiData);

      if (!updatedUser) {
        throw new AppError(
          "Không thể cập nhật thông tin người dùng",
          ErrorType.SERVER_ERROR
        );
      }

      return transformUserData(updatedUser);
    } catch (error: any) {
      console.error("Lỗi khi cập nhật profile:", error);

      // Phân loại lỗi để xử lý phù hợp
      if (error instanceof AppError) {
        throw error;
      }

      // Xử lý lỗi từ API và chuyển đổi thành lỗi ứng dụng
      if (error.status === 401 || error.status === 403) {
        throw new AppError(
          "Không có quyền cập nhật thông tin người dùng",
          ErrorType.AUTHENTICATION_ERROR,
          error.status
        );
      } else if (error.status === 400) {
        throw new AppError(
          "Dữ liệu cập nhật không hợp lệ",
          ErrorType.VALIDATION_ERROR,
          error.status
        );
      } else if (error.status >= 500) {
        throw new AppError(
          "Lỗi máy chủ khi cập nhật thông tin người dùng",
          ErrorType.SERVER_ERROR,
          error.status
        );
      } else {
        throw new AppError(
          "Lỗi không xác định khi cập nhật thông tin người dùng",
          ErrorType.UNKNOWN_ERROR
        );
      }
    }
  },

  /**
   * Đổi mật khẩu người dùng
   * @param currentPassword - Mật khẩu hiện tại
   * @param newPassword - Mật khẩu mới
   * @returns Promise chứa thông báo thành công
   * @throws AppError nếu có lỗi khi đổi mật khẩu
   */
  changePassword: async (
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> => {
    try {
      if (!currentPassword || !newPassword) {
        throw new AppError(
          "Mật khẩu hiện tại hoặc mật khẩu mới không được để trống",
          ErrorType.VALIDATION_ERROR
        );
      }

      return await post<{ message: string }>("/users/me/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
    } catch (error: any) {
      console.error("Lỗi khi đổi mật khẩu:", error);

      // Phân loại lỗi để xử lý phù hợp
      if (error instanceof AppError) {
        throw error;
      }

      // Xử lý lỗi từ API và chuyển đổi thành lỗi ứng dụng
      if (error.status === 401 || error.status === 403) {
        throw new AppError(
          "Không có quyền đổi mật khẩu",
          ErrorType.AUTHENTICATION_ERROR,
          error.status
        );
      } else if (error.status === 400) {
        throw new AppError(
          "Mật khẩu hiện tại không chính xác",
          ErrorType.VALIDATION_ERROR,
          error.status
        );
      } else if (error.status >= 500) {
        throw new AppError(
          "Lỗi máy chủ khi đổi mật khẩu",
          ErrorType.SERVER_ERROR,
          error.status
        );
      } else {
        throw new AppError(
          "Lỗi không xác định khi đổi mật khẩu",
          ErrorType.UNKNOWN_ERROR
        );
      }
    }
  },
};

export default profileService;
