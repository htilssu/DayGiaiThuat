export interface Course {
  id: number;
  title: string;
  description?: string;
  thumbnailUrl?: string;
  level?: string;
  duration?: number;
  price?: number;
  isPublished?: boolean;
  tags?: string;
  requirements?: string;
  whatYouWillLearn?: string;
  createdAt: string;
  updatedAt: string;
  testGenerationStatus?: string;
  isEnrolled?: boolean;
}
