export type ContentType = "topic" | "lesson" | "exercise" | "quiz";

export interface ContentFormData {
  topic: {
    name: string;
    description: string;
    courseId: number;
    order: number;
    externalId: string;
  };
  lesson: {
    title: string;
    description: string;
    topicId: number;
    order: number;
    externalId: string;
    difficultyLevel: string;
    lessonType: string;
    includeExamples: boolean;
    includeExercises: boolean;
    maxSections: number;
  };
  exercise: {
    lessonId: number;
    difficulty: string;
    sessionId: string;
    topicId?: number;
  };
  quiz: {
    lessonId: number;
    questionCount: number;
    difficulty: string;
  };
}

export interface ContentOption {
  type: ContentType;
  icon: React.ComponentType<{ size?: number }>;
  label: string;
  description: string;
  color: string;
}
