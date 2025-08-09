import { get } from "./client";

export interface UserStats {
    level: number;
    completedExercises: number;
    completedCourses: number;
    totalPoints: number;
    streak: number;
}

export interface LearningProgress {
    algorithms: number;
    dataStructures: number;
    dynamicProgramming: number;
}

export interface CourseProgress {
    id: number;
    name: string;
    progress: number;
    colorFrom: string;
    colorTo: string;
}

export interface Badge {
    id: number;
    name: string;
    icon: string;
    description: string;
    unlocked: boolean;
}

export interface Activity {
    id: number;
    name: string;
    type: "exercise" | "course" | "discussion";
    date: string;
    score?: number;
    progress?: string;
}

export interface UserProfile {
    id: number;
    username: string;
    fullName: string;
    email: string;
    avatar: string | null;
    bio: string;
    stats: UserStats;
    learningProgress: LearningProgress;
    courses: CourseProgress[];
    badges: Badge[];
    activities: Activity[];
}

/**
 * Lấy thông tin profile của người dùng hiện tại
 * @returns Thông tin profile của người dùng
 */
async function getProfile() {
    return get<UserProfile>('/users/me/profile');
}

export const profileApi = {
    getProfile,
};

