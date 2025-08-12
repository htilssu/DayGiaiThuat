/**
 * Kiểu dữ liệu cho review topic của khóa học
 */

export interface TopicSkill {
    id: string;
    name: string;
    description: string;
}

export interface TopicReview {
    id: string;
    name: string;
    description: string;
    prerequisites: string[];
    skills: TopicSkill[];
    lessons: any[];
    tests: any[];
    order: number;
}

export interface CourseTopicsReview {
    id: string;
    courseId: number;
    sessionId: string;
    duration: number;
    description: string;
    topics: TopicReview[];
}

export interface UpdateTopicRequest {
    topics: TopicReview[];
}

export interface UpdateTopicItem {
    name: string;
    description: string;
    prerequisites: string[];
}