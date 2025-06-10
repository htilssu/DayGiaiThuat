export interface Discussion {
  id: number;
  title: string;
  content: string;
  author: string;
  createdAt: string;
  updatedAt: string;
  replies: number;
  category: string;
}

export interface CreateDiscussionDto {
  title: string;
  content: string;
  category: string;
}

export interface UpdateDiscussionDto {
  title?: string;
  content?: string;
  category?: string;
}

export interface DiscussionFilters {
  search?: string;
  category?: string;
  sortBy?: "newest" | "oldest" | "most-replies";
  page?: number;
  limit?: number;
}

export interface DiscussionResponse {
  discussions: Discussion[];
  total: number;
  page: number;
  totalPages: number;
}
