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
import { sendReviewChatMessage, CourseReview } from "@/lib/api/admin-courses";
import { notifications } from '@mantine/notifications';

interface CourseReviewChatProps {
    courseId: string;
    reviewData: CourseReview;
    onContentUpdate?: () => void;
}

interface ChatMessage {
    role: "user" | "assistant";
    content: string;
    timestamp: string;
}

export default function CourseReviewChat({
    courseId,
    reviewData,
    onContentUpdate,
}: CourseReviewChatProps) {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: "assistant",
            content: `Xin chào! Tôi là AI Agent hỗ trợ review khóa học (ID: ${courseId}). Tôi có thể giúp bạn:

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
        const currentInput = input;
        setInput("");
        setIsLoading(true);

        try {
            // Call API to send message to review chat
            const response = await sendReviewChatMessage(parseInt(courseId), {
                message: currentInput,
                context: {
                    courseData: { courseId: parseInt(courseId) },
                    generatedContent: reviewData.generatedContent,
                },
            });

            setMessages((prev) => [...prev, response.message]);

            // If the response includes updated content, refresh the parent
            if (response.updatedContent && onContentUpdate) {
                onContentUpdate();
                notifications.show({
                    title: 'Cập nhật nội dung',
                    message: 'Nội dung đã được cập nhật theo yêu cầu của bạn',
                    color: 'blue',
                });
            }
        } catch (error: any) {
            const errorMessage: ChatMessage = {
                role: "assistant",
                content: "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại.",
                timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, errorMessage]);

            notifications.show({
                title: 'Lỗi',
                message: error.message || 'Có lỗi xảy ra khi gửi tin nhắn',
                color: 'red',
            });
        } finally {
            setIsLoading(false);
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
