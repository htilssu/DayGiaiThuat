import { API_URL } from "./client";


async function sendChat(sessionId: string, question: string, type: string, contextId?: string) {
  const response = await fetch(`${API_URL}/tutor/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      },
    credentials: 'include', // Ensure cookies are sent with the request
    body: JSON.stringify({ sessionId, question, type, contextId }),
  });

  if (!response.ok) {
    throw new Error('Network response was not ok');
  }

  return response.body;
}

export const tutorApi = {
    sendChat
}