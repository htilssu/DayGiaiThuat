"use client";

import { useState } from "react";
import {
  Box,
  Paper,
  TextInput,
  ActionIcon,
  LoadingOverlay,
  Divider,
  Stack,
  Text,
  ScrollArea,
} from "@mantine/core";
import { IconSend } from "@tabler/icons-react";
import { ChatMessage as ChatMessageComponent } from "./ChatMessage";
import { useAdminChat } from "./useAdminChat";

interface AdminChatProps {
  // Optional props for future extensibility
  placeholder?: string;
  height?: string | number;
  courseId?: number;
}

export default function AdminChat({
  placeholder = "Nhập tin nhắn cho AI Agent...",
  height = "500px",
  courseId
}: AdminChatProps) {
  const {
    messages,
    input,
    setInput,
    isLoading,
    handleSend,
    messagesEndRef
  } = useAdminChat(courseId);

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Stack h={height} gap={0} style={{ position: 'relative' }}>
      <ScrollArea flex={1} p="md" style={{ height: '100%' }}>
        <Stack gap="md">
          {messages.length === 0 && (
            <Box ta="center" py="xl">
              <Text size="sm" c="dimmed" style={{ fontWeight: 400 }}>
                Chưa có tin nhắn nào. Hãy bắt đầu trò chuyện với AI Agent!
              </Text>
            </Box>
          )}
          {messages.map((message, index) => (
            <ChatMessageComponent key={index} message={message} />
          ))}
          {isLoading && (
            <Box ta="center" py="md">
              <Text size="sm" c="dimmed">
                AI đang suy nghĩ...
              </Text>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Stack>
      </ScrollArea>

      <Divider />

      <Box p="md">
        <Box style={{ display: "flex", gap: "8px" }}>
          <TextInput
            flex={1}
            placeholder={placeholder}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <ActionIcon
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            variant="filled"
            size="lg"
          >
            <IconSend size={16} />
          </ActionIcon>
        </Box>
      </Box>

      <LoadingOverlay visible={isLoading} />
    </Stack>
  );
}