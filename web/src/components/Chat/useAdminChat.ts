import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/lib/api/chat";
import { GoogleGenAI } from "@google/genai";

export function useAdminChat(courseId?: number) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const ai = new GoogleGenAI({
    apiKey: "AIzaSyAoWvIFmtiL1MwP1y8ariEm61Zaq4-uNZo",
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setInput("");
    setIsLoading(true);

    try {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-05-20",
        contents: input,
        config: {
          systemInstruction:
            "You are a professional algorithm expert. You professionally create algorithm exercises. Your mission is to think of clear, concise and life related topic for the student to practice algorithm.",
        },
      });

      if (response.text) {
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: response.text,
          timestamp: new Date().toISOString(),
        };
        addMessage(assistantMessage);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "❌ Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };
      addMessage(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return {
    messages,
    input,
    setInput,
    isLoading,
    messagesEndRef,
    handleSend,
    handleKeyPress,
    addMessage,
  };
}
