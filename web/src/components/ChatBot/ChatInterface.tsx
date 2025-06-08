"use client";

import { useState } from "react";
import { IconSend, IconRobot } from "@tabler/icons-react";
import { TextInput, Text, ScrollArea } from "@mantine/core";
import { GoogleGenAI } from "@google/genai";

export default function ChatInterface() {
  const [messages, setMessages] = useState<
    Array<{ text: string; isUser: boolean }>
  >([
    {
      text: "Hế lu! Học viên yêu dấu có câu hỏi gì nà?",
      isUser: false,
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  // const messagesEndRef = useRef<HTMLDivElement>(null);
  const ai = new GoogleGenAI({
    apiKey: "AIzaSyAoWvIFmtiL1MwP1y8ariEm61Zaq4-uNZo",
  });

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessage = { text: input, isUser: true };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-05-20",
        contents: input,
        config: {
          systemInstruction:
            "Bạn là một giảng viên dạy thuật toán chuyên nghiệp và thân thiện. Nhiệm vụ của bạn là giao tiếp và hỗ trợ giải đáp thắc mắc của học viên",
        },
      });

      if (response.text) {
        const aiMessage = {
          text: response.text,
          isUser: false,
        };
        setMessages((prev) => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      // Add error message to chat
      setMessages((prev) => [
        ...prev,
        {
          text: "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
          isUser: false,
        },
      ]);
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
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-6 bg-gradient-to-r from-[rgb(var(--color-primary))] to-[rgb(var(--color-secondary))]">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/10 rounded-lg">
            <IconRobot size={24} className="text-white" />
          </div>
          <div>
            <Text className="font-medium text-white">AI Assistant</Text>
            <Text size="xs" className="text-white/80">
              Luôn sẵn sàng hỗ trợ bạn
            </Text>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4 custom-scrollbar">
        <div className="flex flex-col gap-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.isUser ? "justify-end" : "justify-start"
              } items-end gap-2`}>
              {!message.isUser && (
                <div className="w-6 h-6 rounded-full bg-[rgb(var(--color-primary))] flex items-center justify-center">
                  <IconRobot size={14} className="text-white" />
                </div>
              )}
              <div
                className={`
                  max-w-[80%] p-3 rounded-2xl
                  ${
                    message.isUser
                      ? "bg-[rgb(var(--color-primary))] text-white rounded-br-sm"
                      : "bg-[rgb(var(--color-primary))]/10 rounded-bl-sm"
                  }
                `}>
                <Text size="sm">{message.text}</Text>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t border-[rgb(var(--color-primary))]/10">
        <TextInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Nhập tin nhắn của bạn..."
          className="focus-within:ring-2 ring-[rgb(var(--color-primary))]/20 rounded-full"
          rightSection={
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              aria-label="Gửi tin nhắn"
              className={`
                p-1.5 rounded-full mr-1
                ${
                  input.trim() && !isLoading
                    ? "text-[rgb(var(--color-primary))] hover:bg-[rgb(var(--color-primary))]/10"
                    : "text-gray-400"
                }
                transition-colors duration-200
              `}>
              <IconSend size={18} />
            </button>
          }
          styles={{
            input: {
              borderRadius: "9999px",
              border: "1px solid rgb(var(--color-primary))/20",
              "&:focus": {
                borderColor: "rgb(var(--color-primary))/30",
              },
            },
          }}
        />
      </div>
    </div>
  );
}
