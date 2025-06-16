import { del, get, patch, post } from "@/lib/api";
import {
  CreateDiscussionDto,
  Discussion,
  DiscussionFilters,
  DiscussionResponse,
  UpdateDiscussionDto,
} from "./types";

const DISCUSSIONS_BASE_URL = "/discussions";

export const discussionsApi = {
  getDiscussions: async (
    filters: DiscussionFilters = {}
  ): Promise<DiscussionResponse> => {
    const queryParams = new URLSearchParams();

    if (filters.search) queryParams.append("search", filters.search);
    if (filters.category) queryParams.append("category", filters.category);
    if (filters.sortBy) queryParams.append("sortBy", filters.sortBy);
    if (filters.page) queryParams.append("page", filters.page.toString());
    if (filters.limit) queryParams.append("limit", filters.limit.toString());

    const url = `${DISCUSSIONS_BASE_URL}?${queryParams.toString()}`;
    return get<DiscussionResponse>(url);
  },

  getDiscussion: async (id: number): Promise<Discussion> => {
    return get<Discussion>(`${DISCUSSIONS_BASE_URL}/${id}`);
  },

  createDiscussion: async (data: CreateDiscussionDto): Promise<Discussion> => {
    return post<Discussion>(DISCUSSIONS_BASE_URL, data);
  },

  updateDiscussion: async (
    id: number,
    data: UpdateDiscussionDto
  ): Promise<Discussion> => {
    return patch<Discussion>(`${DISCUSSIONS_BASE_URL}/${id}`, data);
  },

  deleteDiscussion: async (id: number): Promise<void> => {
    return del(`${DISCUSSIONS_BASE_URL}/${id}`);
  },
};
