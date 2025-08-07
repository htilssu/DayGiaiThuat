"use client";

import { useState } from "react";
import {
  Box,
  Paper,
  TextInput,
  ActionIcon,
  LoadingOverlay,
  Divider,
} from "@mantine/core";
import { IconSend } from "@tabler/icons-react";
import { ChatMessage as ChatMessageComponent } from "./ChatMessage";
import { ContentType } from "./types";
import { ContentOptions } from "./ContentOptions";
import { ContentCreationModal } from "./ContentCreationModal";
import { useAdminChat } from "./useAdminChat";
import { useContentCreation } from "./useContentCreation";

export function AdminChat() {
  const [showContentModal, setShowContentModal] = useState(false);
  const [selectedContentType, setSelectedContentType] =
    useState<ContentType | null>(null);

  const {
    messages,
    input,
    setInput,
    isLoading,
    messagesEndRef,
    handleSend,
    handleKeyPress,
    addMessage,
  } = useAdminChat();

  const { formData, setFormData, resetFormData, createContent } =
    useContentCreation();

  const handleContentTypeSelect = (type: ContentType) => {
    setSelectedContentType(type);
    setShowContentModal(true);
  };

  const handleCreateContent = async () => {
    if (!selectedContentType) return;

    const userMessage = {
      role: "user" as const,
      content: `Creating ${selectedContentType}...`,
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    setShowContentModal(false);

    await createContent(
      selectedContentType,
      (successMessage) => {
        addMessage(successMessage);
        resetFormData();
      },
      (errorMessage) => {
        addMessage(errorMessage);
        resetFormData();
      }
    );
  };

  const handleModalClose = () => {
    setShowContentModal(false);
    setSelectedContentType(null);
    resetFormData();
  };

  return (
    <>
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

        <Divider my="md" />

        <ContentOptions onContentTypeSelect={handleContentTypeSelect} />

        <Box p="xs">
          <TextInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Or type your message to chat with AI..."
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

      <ContentCreationModal
        opened={showContentModal}
        onClose={handleModalClose}
        contentType={selectedContentType}
        formData={formData}
        onFormDataChange={setFormData}
        onCreateContent={handleCreateContent}
        isLoading={isLoading}
      />
    </>
  );
}
