export interface Course {
  id: number;
  title: string;
  description?: string;
  thumbnail_url?: string;
  level?: string;
  duration?: number;
  price?: number;
  is_published?: boolean;
  tags?: string;
  requirements?: string;
  what_you_will_learn?: string;
  created_at: string;
  updated_at: string;
  test_generation_status?: string;
  is_enrolled?: boolean;
}
