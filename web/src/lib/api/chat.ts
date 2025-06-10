import { client } from "./client";

export interface ChatMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: ChatMessage;
}

const chatApi = {
  sendMessage: async (message: string): Promise<ChatResponse> => {
    const response = await client.post<ChatResponse>("/api/chat", {
      message,
    });
    return response.data;
  },
};

export default chatApi;
