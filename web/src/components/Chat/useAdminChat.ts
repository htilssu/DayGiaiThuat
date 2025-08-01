import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/lib/api/chat";
import { GoogleGenAI } from "@google/genai";

export function useAdminChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);


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
}
