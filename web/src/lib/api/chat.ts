import { post } from "./client";

export interface ChatMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: ChatMessage;
}

export const chatApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const response = await post<ChatResponse>("/api/chat", {
      message,
    });
    return response;
  },
};

