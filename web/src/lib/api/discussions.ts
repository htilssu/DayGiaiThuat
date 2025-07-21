import { get, post, patch, del } from "./client";

export interface Discussion {
  id: number;
  title: string;
  content: string;
  author: string;
  category: string;
  createdAt: string;
  updatedAt: string;
  replies: number;
}

export interface DiscussionsResponse {
  discussions: Discussion[];
  total: number;
  page: number;
  totalPages: number;
}

export interface GetDiscussionsParams {
  search?: string;
  category?: string;
  sortBy?: "newest" | "oldest" | "most-replies";
  page?: number;
  limit?: number;
}

export interface CreateDiscussionParams {
  title: string;
  content: string;
  category: string;
}

export interface UpdateDiscussionParams {
  title?: string;
  content?: string;
  category?: string;
}

export const discussionsApi = {
  getDiscussions: async (
    params: GetDiscussionsParams = {}
  ): Promise<DiscussionsResponse> => {
    // Build query string
    const query = new URLSearchParams();
    if (params.search) query.append("search", params.search);
    if (params.category) query.append("category", params.category);
    if (params.sortBy) query.append("sort_by", params.sortBy);
    if (params.page) query.append("page", params.page.toString());
    if (params.limit) query.append("limit", params.limit.toString());
    const url = `/discussions?${query.toString()}`;
    return get<DiscussionsResponse>(url);
  },

  getDiscussion: async (id: number): Promise<Discussion> => {
    return get<Discussion>(`/discussions/${id}`);
  },

  createDiscussion: async (
    data: CreateDiscussionParams
  ): Promise<Discussion> => {
    return post<Discussion>("/discussions", data);
  },

  updateDiscussion: async (
    id: number,
    data: UpdateDiscussionParams
  ): Promise<Discussion> => {
    return patch<Discussion>(`/discussions/${id}`, data);
  },

  deleteDiscussion: async (id: number): Promise<void> => {
    return del<void>(`/discussions/${id}`);
  },
};
