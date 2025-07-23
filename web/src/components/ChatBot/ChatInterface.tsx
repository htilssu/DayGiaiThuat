"use client";

import { tutorApi } from "@/lib/api/tutor";
import { ScrollArea, Text, TextInput } from "@mantine/core";
import { IconRobot, IconSend } from "@tabler/icons-react";
import { useEffect, useRef, useState } from "react";
import LoadingDots from "./LoadingDots";
import { useAppSelector } from "@/lib/store";
import { MarkdownRenderer } from "../ui/MarkdownRenderer";

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
  const viewport = useRef<HTMLDivElement>(null);
  const tutorState = useAppSelector((state) => state.tutor);

  useEffect(() => {
    // Scroll to bottom whenever messages change or loading state changes
    if (viewport.current) {
      viewport.current.scrollTo({
        top: viewport.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const newMessage = { text: input, isUser: true };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setIsLoading(true);

    try {
      console.log("Sending message to tutor API:", input);
      const response = await tutorApi.sendChat(
        tutorState.sessionId!,
        input,
        tutorState.type,
        tutorState.contextId!
      );

      if (!response || !response.getReader) {
        throw new Error("Invalid response from API");
      }

      const reader = response.getReader();
      const decoder = new TextDecoder();

      if (reader) {
        let botMessage = '';

        // Add empty bot message to update in real-time
        setMessages(prev => [...prev, { text: '', isUser: false }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          console.log("Received chunk:", chunk);
          botMessage += chunk;

          // Update the last message (bot's response) in real-time
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1] = { text: botMessage, isUser: false };
            return newMessages;
          });
        }
      }
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
            <Text className="font-medium text-white">Gia sư</Text>
            <Text size="xs" className="text-white/80">
              Bạn có thắc mắc gì không?
            </Text>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <ScrollArea
        viewportRef={viewport}
        className="flex-1 p-4 custom-scrollbar">
        <div className="flex flex-col gap-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.isUser ? "justify-end" : "justify-start"
                } items-end gap-2`}>
              {!message.isUser && (
                <div className="w-6 h-6 rounded-full bg-[rgb(var(--color-primary))] flex items-center justify-center">
                  <IconRobot size={14} className="text-white" />
                </div>
              )}
              <div
                className={`
                  max-w-[80%] p-3 rounded-2xl
                  ${message.isUser
                    ? "bg-[rgb(var(--color-primary))] text-white rounded-br-sm"
                    : "bg-[rgb(var(--color-primary))]/10 rounded-bl-sm"
                  }
                `}>
                <MarkdownRenderer content={message.text} />
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex items-end gap-2">
              <div className="w-6 h-6 rounded-full bg-[rgb(var(--color-primary))] flex items-center justify-center">
                <IconRobot size={14} className="text-white" />
              </div>
              <div className="p-3 rounded-2xl bg-[rgb(var(--color-primary))]/10 rounded-bl-sm">
                <LoadingDots />
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t border-[rgb(var(--color-primary))]/10">
        <TextInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Nhập tin nhắn của bạn..."
          className="ring-2 ring-[rgb(var(--color-primary))]/20 rounded-full"
          rightSection={
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              aria-label="Gửi tin nhắn"
              className={`
                p-1.5 rounded-full mr-1
                ${input.trim() && !isLoading
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
