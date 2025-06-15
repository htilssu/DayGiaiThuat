import { get, post, put } from "@/lib/api/client";

/**
 * Loại hoạt động của người dùng
 */
export type ActivityType =
  | "exercise"
  | "course"
  | "discussion"
  | "badge"
  | "level_up";

/**
 * Interface cho thông tin cá nhân cơ bản của người dùng
 */
export interface BasicUserInfo {
  id: number;
  username: string;
  email: string;
  fullName: string;
  bio?: string;
  avatarUrl?: string;
}

/**
 * Interface cho thông tin tài khoản người dùng
 */
export interface AccountInfo {
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
  isVerified: boolean;
  lastLogin?: string;
  preferences?: any;
}

/**
 * Interface cho thống kê người dùng
 */
export interface UserStats {
  completedExercises: number;
  completedCourses: number;
  totalPoints: number;
  streakDays: number;
  level: number;
  problemsSolved: number;
}

/**
 * Interface cho huy hiệu người dùng
 */
export interface Badge {
  id: number;
  name: string;
  icon: string;
  description: string;
  unlocked: boolean;
}

/**
 * Interface cho hoạt động người dùng
 */
export interface Activity {
  id: number;
  type: ActivityType;
  name: string;
  date: string;
  score?: string;
  progress?: string;
}

/**
 * Interface cho tiến độ học tập
 */
export interface LearningProgress {
  algorithms: number;
  dataStructures: number;
  dynamicProgramming: number;
}

/**
 * Interface cho thông tin khóa học
 */
export interface CourseItem {
  id: string;
  name: string;
  progress: number;
  colorFrom: string;
  colorTo: string;
  imageUrl?: string;
}

/**
 * Interface định nghĩa dữ liệu người dùng đầy đủ
 * Đây là interface chính được sử dụng xuyên suốt ứng dụng
 */
export interface ProfileData extends BasicUserInfo, AccountInfo {
  // Thống kê người dùng
  stats: UserStats;

  // Danh sách thành tích
  badges: Array<Badge>;

  // Lịch sử hoạt động
  activities: Array<Activity>;

  // Tiến độ học tập
  learningProgress: LearningProgress;

  // Tiến độ khóa học
  courseProgress: Array<CourseItem>;
}

/**
 * Interface đơn giản hóa cho dữ liệu từ AuthContext
 */
export interface AuthUserData extends Partial<ProfileData> {
  id: number;
  username: string;
  email: string;
  isActive: boolean;
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
 * Interface cho thống kê người dùng đã được chuyển đổi
 */
export interface TransformedUserStats {
  completedExercises: number;
  completedCourses: number;
  totalPoints: number;
  streak: number; // Thay cho streakDays
  level: number;
  problemsSolved: number;
}

/**
 * Interface để thay thế cho dữ liệu về tiến độ khóa học (courseProgress) trong TransformedUserData
 */
export interface TransformedCourseData extends Omit<CourseItem, "imageUrl"> {
  imageUrl: string; // Chuyển từ optional thành required
}

/**
 * Interface cho việc hiển thị profile người dùng
 * Mở rộng từ ProfileData với một số trường bổ sung
 */
export interface TransformedUserData
  extends Omit<BasicUserInfo, "avatarUrl">,
  Omit<AccountInfo, "preferences"> {
  bio: string; // Đảm bảo là required thay vì optional
  preferences: any; // Đảm bảo là required thay vì optional

  // Các trường khác từ ProfileData
  badges: Array<Badge>;
  activities: Array<Activity>;
  learningProgress: LearningProgress;

  // Trường hiển thị bổ sung
  joinDate: string;
  avatar: string; // Thay cho avatarUrl

  // Đổi tên trường
  courses: Array<TransformedCourseData>;

  // Sửa cấu trúc stats
  stats: TransformedUserStats;
}

/**
 * Interface cho dữ liệu cập nhật profile người dùng
 */
export interface ProfileUpdateData {
  fullName?: string;
  bio?: string;
  avatarUrl?: string;
}

/**
 * Chuyển đổi dữ liệu từ API sang dạng dữ liệu frontend thân thiện
 * @param userData Dữ liệu người dùng từ API
 * @returns TransformedUserData với tên trường đã được chuyển đổi
 */
export const transformUserData = (
  userData: ProfileData
): TransformedUserData => {
  if (!userData) {
    throw new AppError(
      "Dữ liệu người dùng không hợp lệ",
      ErrorType.VALIDATION_ERROR
    );
  }

  // Kiểm tra và chuẩn bị các trường dữ liệu cần thiết
  const stats = userData.stats || {};
  const learningProgress = userData.learningProgress || {};
  const courseProgress = userData.courseProgress || [];
  const activities = userData.activities || [];

  return {
    id: userData.id,
    username: userData.username,
    email: userData.email,
    fullName: userData.fullName,
    isActive: userData.isActive,
    isVerified: userData.isVerified,
    createdAt: userData.createdAt,
    updatedAt: userData.updatedAt,
    bio: userData.bio || "",
    avatar: userData.avatarUrl || "/placeholder-avatar.png",
    lastLogin: userData.lastLogin,
    preferences: userData.preferences || {},
    joinDate: new Date(userData.createdAt).toLocaleDateString("vi-VN"),
    stats: {
      completedExercises: stats.completedExercises || 0,
      completedCourses: stats.completedCourses || 0,
      totalPoints: stats.totalPoints || 0,
      streak: stats.streakDays || 0,
      level: stats.level || 1,
      problemsSolved: stats.problemsSolved || 0,
    },
    badges: userData.badges || [],
    activities: activities,
    learningProgress: {
      algorithms: learningProgress.algorithms || 0,
      dataStructures: learningProgress.dataStructures || 0,
      dynamicProgramming: learningProgress.dynamicProgramming || 0,
    },
    courses: (courseProgress || []).map((course) => ({
      id: course.id,
      name: course.name,
      progress: course.progress,
      colorFrom: course.colorFrom,
      colorTo: course.colorTo,
      imageUrl: course.imageUrl || "/placeholder-course.png",
    })),
  };
};

/**
 * Tạo ProfileData cơ bản từ thông tin user trong AuthContext
 * @param userData Dữ liệu người dùng từ AuthContext
 * @returns ProfileData đã được chuyển đổi sang định dạng frontend
 * @throws AppError nếu dữ liệu không hợp lệ
 */
export const createBasicProfileFromAuth = (
  userData: AuthUserData
): TransformedUserData => {
  if (!userData) {
    throw new AppError(
      "Dữ liệu người dùng không hợp lệ",
      ErrorType.VALIDATION_ERROR
    );
  }

  // Nếu userData đã có đầy đủ dữ liệu, chuyển đổi nó
  if (userData.stats && userData.learningProgress && userData.courseProgress) {
    return transformUserData(userData as ProfileData);
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
  getProfile: async (userId?: number): Promise<TransformedUserData> => {
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
  updateProfile: async (
    profileData: ProfileUpdateData
  ): Promise<TransformedUserData> => {
    try {
      if (!profileData) {
        throw new AppError(
          "Dữ liệu cập nhật không hợp lệ",
          ErrorType.VALIDATION_ERROR
        );
      }

      const updatedUser = await put<ProfileData>("/users/me", profileData);

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
        currentPassword,
        newPassword,
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
