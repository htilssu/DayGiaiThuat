import { get, post, patch, del } from "./client";

export type Reply = {
  id: number;
  discussionId: number;
  userId: number;
  author: string;
  content: string;
  createdAt: string;
  updatedAt: string;
};

export type ReplyListResponse = {
  replies: Reply[];
  total: number;
};

export type CreateReplyParams = {
  discussionId: number;
  content: string;
};

export type UpdateReplyParams = {
  content?: string;
};

export const repliesApi = {
  /**
   * Create a new reply for a discussion
   */
  createReply: async (data: CreateReplyParams): Promise<Reply> => {
    return post<Reply>("/replies/", data);
  },

  /**
   * Get all replies for a specific discussion
   */
  getRepliesByDiscussion: async (
    discussionId: number
  ): Promise<ReplyListResponse> => {
    return get<ReplyListResponse>(`/replies/discussion/${discussionId}`);
  },

  /**
   * Update a reply (only by the author)
   */
  updateReply: async (
    replyId: number,
    data: UpdateReplyParams
  ): Promise<Reply> => {
    return patch<Reply>(`/replies/${replyId}`, data);
  },

  /**
   * Delete a reply (only by the author)
   */
  deleteReply: async (replyId: number): Promise<void> => {
    return del<void>(`/replies/${replyId}`);
  },
};
