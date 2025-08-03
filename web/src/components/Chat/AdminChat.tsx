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

interface AdminChatProps {
  courseData?: any;
  generatedContent?: any;
  onContentUpdate?: (newContent: any) => void;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export default function AdminChat({
  courseData,
  generatedContent,
  onContentUpdate,
}: AdminChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: `Xin chào! Tôi là AI Agent hỗ trợ tạo nội dung khóa học "${courseData?.title}". Tôi có thể giúp bạn:

• Chỉnh sửa nội dung đã tạo
• Tạo thêm topics, bài học, bài tập
• Điều chỉnh độ khó và cấu trúc
• Giải thích chi tiết về nội dung

Bạn có muốn thay đổi gì về nội dung đã tạo không?`,
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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
      // Simulate AI response
      await new Promise((resolve) => setTimeout(resolve, 1500));

      const aiResponse: ChatMessage = {
        role: "assistant",
        content: generateAIResponse(input, courseData, generatedContent),
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, aiResponse]);

      // If the user asks for content changes, simulate content update
      if (
        input.toLowerCase().includes("thêm") ||
        input.toLowerCase().includes("tạo") ||
        input.toLowerCase().includes("sửa")
      ) {
        handleContentChange(input);
      }
    } catch (error) {
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Xin lỗi, tôi gặp lỗi. Vui lòng thử lại.",
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateAIResponse = (
    userInput: string,
    courseData: any,
    content: any
  ): string => {
    const input = userInput.toLowerCase();

    if (input.includes("thêm topic") || input.includes("tạo topic")) {
      return `Tôi sẽ thêm một topic mới vào khóa học. Dựa trên nội dung hiện tại, tôi đề xuất thêm topic "Thực hành nâng cao" với các bài học chi tiết hơn. Topic này sẽ bao gồm:

• Các bài tập thực hành phức tạp
• Case study thực tế
• Dự án mini để áp dụng kiến thức

Tôi đã cập nhật nội dung, bạn có thể xem bên trái.`;
    }

    if (input.includes("sửa") || input.includes("chỉnh sửa")) {
      return `Tôi có thể giúp bạn chỉnh sửa nội dung. Bạn muốn sửa phần nào cụ thể?

• Tiêu đề và mô tả các topic
• Thời lượng bài học
• Độ khó bài tập
• Nội dung chi tiết

Hãy cho tôi biết chi tiết hơn về những gì bạn muốn thay đổi.`;
    }

    if (input.includes("độ khó") || input.includes("khó")) {
      return `Tôi hiểu bạn muốn điều chỉnh độ khó. Hiện tại khóa học được thiết kế cho level ${courseData?.level}.

Tôi có thể:
• Tăng/giảm độ phức tạp của bài tập
• Thêm/bớt các concepts nâng cao
• Điều chỉnh tốc độ tiến trình học

Bạn muốn làm khóa học dễ hơn hay khó hơn?`;
    }

    if (input.includes("bài tập") || input.includes("exercise")) {
      return `Về bài tập, tôi có thể:

• Tạo thêm bài tập thực hành
• Thay đổi format bài tập (trắc nghiệm, tự luận, coding)
• Điều chỉnh độ khó từng bài
• Thêm hints và gợi ý

Hiện tại có ${content?.exercises?.length || 0} bài tập. Bạn muốn thêm loại bài tập nào?`;
    }

    return `Tôi hiểu yêu cầu của bạn về "${userInput}". Đây là một ý tưởng hay để cải thiện khóa học "${courseData?.title}".

Tôi sẽ phân tích và đưa ra đề xuất cụ thể. Bạn có thể mô tả chi tiết hơn về những gì bạn mong muốn không?

Một số gợi ý bạn có thể hỏi:
• "Thêm một topic về [chủ đề cụ thể]"
• "Làm bài tập khó hơn/dễ hơn"
• "Tạo thêm ví dụ thực tế"
• "Sửa mô tả topic [tên topic]"`;
  };

  const handleContentChange = (userInput: string) => {
    if (!onContentUpdate || !generatedContent) return;

    const input = userInput.toLowerCase();

    if (input.includes("thêm topic")) {
      const newTopic = {
        id: Date.now(),
        name: "Thực hành nâng cao",
        description: "Topic mới được tạo theo yêu cầu của admin",
        order: generatedContent.topics.length + 1,
        duration: 45,
      };

      const newLesson = {
        id: Date.now() + 1,
        topicId: newTopic.id,
        name: "Bài học thực hành nâng cao",
        content: "Nội dung bài học chi tiết...",
        duration: 25,
      };

      const newExercise = {
        id: Date.now() + 2,
        topicId: newTopic.id,
        name: "Bài tập thực hành nâng cao",
        description: "Bài tập áp dụng kiến thức vào thực tế",
        difficulty: "Medium",
      };

      const updatedContent = {
        ...generatedContent,
        topics: [...generatedContent.topics, newTopic],
        lessons: [...generatedContent.lessons, newLesson],
        exercises: [...generatedContent.exercises, newExercise],
      };

      onContentUpdate(updatedContent);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Stack h="100%" gap={0}>
      <ScrollArea flex={1} p="md">
        <Stack gap="md">
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
        </Stack>
      </ScrollArea>

      <Divider />

      <Box p="md">
        <Box style={{ display: "flex", gap: "8px" }}>
          <TextInput
            flex={1}
            placeholder="Nhập tin nhắn cho AI Agent..."
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
