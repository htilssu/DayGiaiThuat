"use client";

import { useState, useRef, useEffect } from "react";
import {
  Box,
  Paper,
  TextInput,
  ActionIcon,
  LoadingOverlay,
} from "@mantine/core";
import { IconSend } from "@tabler/icons-react";
import { ChatMessage as ChatMessageComponent } from "./ChatMessage";
import { ChatMessage } from "@/lib/api/chat";
import { GoogleGenAI } from "@google/genai";

export function Chat() {
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

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // const response = await api.chat.sendMessage(input);
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
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
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

  return (
    <Paper
      shadow="sm"
      p="md"
      style={{
        height: "600px",
        display: "flex",
        flexDirection: "column",
      }}>
      <Box
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "1rem",
          position: "relative",
        }}>
        <LoadingOverlay visible={isLoading} />
        {messages.map((message, index) => (
          <ChatMessageComponent key={index} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </Box>
      <Box p="xs">
        <TextInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Type your message..."
          rightSection={
            <ActionIcon
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              variant="filled"
              size="lg">
              <IconSend size="1.2rem" />
            </ActionIcon>
          }
        />
      </Box>
    </Paper>
  );
}
