import { post } from "@/lib/api/client";

export type AIChatRequest = {
  code: string;
  results: any[];
  title: string;
  userMessage?: string;
  allTestsPassed?: boolean;
};

export type AIChatResponse = {
  reply: string;
};

export async function sendAIChatRequest(
  data: AIChatRequest
): Promise<AIChatResponse> {
  return post<AIChatResponse>("/ai-chat/", {
    code: data.code,
    results: data.results,
    title: data.title,
    user_message: data.userMessage,
    all_tests_passed: data.allTestsPassed,
  });
}
