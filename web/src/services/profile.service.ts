import api from "@/lib/api";
import { get, post, put } from "@/lib/api/client";

/**
 * Interface định nghĩa dữ liệu thống kê người dùng
 */
export interface UserStats {
  completedExercises: number;
  completedCourses: number;
  totalPoints: number;
  streak: number;
  level: number;
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
  colorFrom: string;
  colorTo: string;
  imageUrl?: string;
}

/**
 * Interface định nghĩa dữ liệu hoạt động gần đây
 */
export interface Activity {
  id: number;
  type: "exercise" | "course" | "discussion";
  name: string;
  date: string;
  score?: string;
  progress?: string;
}

/**
 * Interface định nghĩa dữ liệu profile đầy đủ
 */
export interface ProfileData {
  id: string;
  username: string;
  email: string;
  fullName: string;
  bio: string;
  avatar: string;
  joinDate: string;
  stats: UserStats;
  badges: Badge[];
  activities: Activity[];
  learningProgress: {
    algorithms: number;
    dataStructures: number;
    dynamicProgramming: number;
  };
  courses: CourseProgress[];
}

/**
 * Interface cho dữ liệu từ API trả về
 */
export interface ProfileResponse {
  id: string;
  username: string;
  email: string;
  full_name: string;
  bio: string;
  avatar_url: string;
  created_at: string;
  stats: {
    completed_exercises: number;
    completed_courses: number;
    total_points: number;
    streak_days: number;
    level: number;
  };
  badges: {
    id: number;
    name: string;
    icon: string;
    description: string;
    unlocked: boolean;
  }[];
  activities: {
    id: number;
    type: string;
    name: string;
    date: string;
    score?: string;
    progress?: string;
  }[];
  learning_progress: {
    algorithms: number;
    data_structures: number;
    dynamic_programming: number;
  };
  courses: {
    id: string;
    name: string;
    progress: number;
    color_from: string;
    color_to: string;
    image_url?: string;
  }[];
}

/**
 * Chuyển đổi dữ liệu từ API response sang định dạng dùng trong ứng dụng
 * @param data Dữ liệu từ API
 * @returns Dữ liệu đã chuyển đổi
 */
const mapProfileResponseToData = (data: ProfileResponse): ProfileData => {
  return {
    id: data.id,
    username: data.username,
    email: data.email,
    fullName: data.full_name,
    bio: data.bio || "",
    avatar: data.avatar_url,
    joinDate: new Date(data.created_at).toLocaleDateString("vi-VN"),
    stats: {
      completedExercises: data.stats.completed_exercises,
      completedCourses: data.stats.completed_courses,
      totalPoints: data.stats.total_points,
      streak: data.stats.streak_days,
      level: data.stats.level,
    },
    badges: data.badges.map((badge) => ({
      id: badge.id,
      name: badge.name,
      icon: badge.icon,
      description: badge.description,
      unlocked: badge.unlocked,
    })),
    activities: data.activities.map((activity) => ({
      id: activity.id,
      type: activity.type as "exercise" | "course" | "discussion",
      name: activity.name,
      date: activity.date,
      score: activity.score,
      progress: activity.progress,
    })),
    learningProgress: {
      algorithms: data.learning_progress.algorithms,
      dataStructures: data.learning_progress.data_structures,
      dynamicProgramming: data.learning_progress.dynamic_programming,
    },
    courses: data.courses.map((course) => ({
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
 * Service quản lý dữ liệu profile người dùng
 */
const profileService = {
  /**
   * Lấy dữ liệu profile người dùng
   * @param userId - ID của người dùng (không bắt buộc, mặc định lấy profile hiện tại)
   * @returns Promise chứa dữ liệu profile
   */
  getProfile: async (userId?: string): Promise<ProfileData> => {
    try {
      // Nếu có userId, gọi API để lấy thông tin người dùng cụ thể
      // Nếu không, lấy thông tin người dùng hiện tại
      const endpoint = userId
        ? `/users/${userId}/profile`
        : "/users/me/profile";
      const profileData = await get<ProfileResponse>(endpoint);
      return mapProfileResponseToData(profileData);
    } catch (error) {
      console.error("Lỗi khi lấy dữ liệu profile:", error);

      // Trả về dữ liệu mẫu nếu API chưa sẵn sàng (chỉ dùng cho phát triển)
      return {
        id: userId || "user-123",
        username: "nguyenvana",
        email: "nguyenvana@example.com",
        fullName: "Nguyễn Văn A",
        bio: "Học viên đam mê thuật toán và lập trình. Đang theo đuổi ngành Khoa học máy tính.",
        avatar: "/placeholder-avatar.png",
        joinDate: "15/04/2023",
        stats: {
          completedExercises: 48,
          completedCourses: 3,
          totalPoints: 1250,
          streak: 15,
          level: 12,
        },
        badges: [
          {
            id: 1,
            name: "Người mới",
            icon: "🔰",
            description: "Hoàn thành đăng ký tài khoản",
            unlocked: true,
          },
          {
            id: 2,
            name: "Siêu sao",
            icon: "⭐",
            description: "Đạt điểm tối đa trong 5 bài tập",
            unlocked: true,
          },
          {
            id: 3,
            name: "Chăm chỉ",
            icon: "🔥",
            description: "Hoạt động 10 ngày liên tiếp",
            unlocked: true,
          },
          {
            id: 4,
            name: "Bậc thầy thuật toán",
            icon: "🏆",
            description: "Hoàn thành 100 bài tập",
            unlocked: false,
          },
        ],
        activities: [
          {
            id: 1,
            type: "exercise",
            name: "Tìm kiếm nhị phân",
            date: "15/04/2025",
            score: "95/100",
          },
          {
            id: 2,
            type: "course",
            name: "Cấu trúc dữ liệu cơ bản",
            date: "10/04/2025",
            progress: "75%",
          },
          {
            id: 3,
            type: "discussion",
            name: "Thuật toán sắp xếp nhanh",
            date: "08/04/2025",
          },
        ],
        learningProgress: {
          algorithms: 75,
          dataStructures: 60,
          dynamicProgramming: 30,
        },
        courses: [
          {
            id: "course-1",
            name: "Cấu trúc dữ liệu nâng cao",
            progress: 35,
            colorFrom: "blue-500",
            colorTo: "purple-600",
          },
          {
            id: "course-2",
            name: "Thuật toán tìm đường đi ngắn nhất",
            progress: 60,
            colorFrom: "green-500",
            colorTo: "teal-600",
          },
        ],
      };
    }
  },

  /**
   * Cập nhật thông tin profile
   * @param data - Dữ liệu cập nhật
   * @returns Promise chứa dữ liệu profile đã cập nhật
   */
  updateProfile: async (data: {
    fullName?: string;
    bio?: string;
    avatar?: string;
  }): Promise<ProfileData> => {
    try {
      // Chuyển đổi dữ liệu từ định dạng frontend sang định dạng API
      const apiData = {
        full_name: data.fullName,
        bio: data.bio,
        avatar_url: data.avatar,
      };

      // Gọi API để cập nhật thông tin
      const updatedProfile = await put<ProfileResponse>(
        "/users/me/profile",
        apiData
      );

      return mapProfileResponseToData(updatedProfile);
    } catch (error) {
      console.error("Lỗi khi cập nhật profile:", error);
      throw error;
    }
  },

  /**
   * Đổi mật khẩu người dùng
   * @param currentPassword - Mật khẩu hiện tại
   * @param newPassword - Mật khẩu mới
   * @returns Promise chứa thông báo thành công
   */
  changePassword: async (
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> => {
    try {
      return await post<{ message: string }>("/users/me/change-password", {
        current_password: currentPassword,
        new_password: newPassword,
      });
    } catch (error) {
      console.error("Lỗi khi đổi mật khẩu:", error);
      throw error;
    }
  },
};

export default profileService;
