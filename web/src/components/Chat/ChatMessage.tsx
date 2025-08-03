import { Avatar, Box, Paper, Text } from "@mantine/core";
import { ChatMessage as ChatMessageType } from "@/lib/api/chat";
import { IconRobot, IconUser } from "@tabler/icons-react";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <Box
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "1rem",
      }}>
      <Box style={{ display: "flex", gap: "1rem", maxWidth: "70%" }}>
        <Avatar>
          {isUser ? <IconUser size="1.5rem" /> : <IconRobot size="1.5rem" />}
        </Avatar>
        <Paper p="md" withBorder style={{ borderRadius: "1rem", minWidth: '120px' }}>
          <Text size="sm" style={{ lineHeight: 1.4, wordBreak: 'break-word' }}>
            {message.content}
          </Text>
        </Paper>
      </Box>
    </Box>
  );
}
