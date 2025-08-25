import { useEffect, useState, useRef } from "react";
import { IconSend } from "@tabler/icons-react";
import { TestResult } from "./types";
import { sendAIChatRequest } from "@/lib/api/aiChat";
import { MarkdownRenderer } from "@/components/ui/MarkdownRenderer";

export default function AIChat({
  code,
  results,
  calling,
  title,
  aiResponse,
  isLoading,
  setIsLoading,
}: {
  code: string;
  results: TestResult[];
  calling: {
    callAIChat: boolean;
    setCallAIChat: (value: boolean) => void;
    allTestsPassed: boolean;
  };
  title: string;
  aiResponse?: string;
  isLoading: boolean;
  setIsLoading: (value: boolean) => void;
}) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<
    Array<{ role: "user" | "assistant"; content: string }>
  >([
    {
      role: "assistant",
      content:
        "Xin chào! Tôi là trợ lý AI. Tôi có thể giúp bạn giải quyết bài tập này. Bạn có câu hỏi gì không?",
    },
  ]);
  const [input, setInput] = useState("");

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await sendAIChatRequest({
        code,
        results,
        title,
        userMessage,
      });
      if (response.reply) {
        const aiMessage: { role: "assistant"; content: string } = {
          role: "assistant",
          content: response.reply,
        };
        setMessages((prev) => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant" as const,
          content: "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (calling.callAIChat) {
      calling.setCallAIChat(false);
    }
  }, [calling.callAIChat]);

  useEffect(() => {
    if (aiResponse) {
      const aiMessage: { role: "assistant"; content: string } = {
        role: "assistant",
        content: aiResponse,
      };
      setMessages((prev) => [...prev, aiMessage]);
    }
  }, [aiResponse]);

  return (
    <div className="flex flex-col h-full border border-foreground/10 rounded-lg overflow-hidden theme-transition bg-background">
      {/* Header */}
      <div className="bg-foreground/5 p-4 border-b border-foreground/10">
        <h3 className="font-semibold text-foreground flex items-center gap-2">
          <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
          Tutor Agent
        </h3>
        <p className="text-sm text-foreground/60 mt-1">
          Hỏi đáp về bài tập và nhận hỗ trợ từ AI
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}>
            <div
              className={`max-w-[85%] rounded-lg px-4 py-3 ${
                message.role === "user"
                  ? "bg-primary text-white shadow-lg"
                  : "bg-foreground/5 text-foreground border border-foreground/20 shadow-sm"
              }`}>
              {message.role === "assistant" ? (
                <div className="prose prose-sm max-w-none">
                  <MarkdownRenderer
                    content={message.content}
                    className="text-foreground"
                  />
                </div>
              ) : (
                <p className="text-sm leading-relaxed">{message.content}</p>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-foreground/5 text-foreground rounded-lg px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:0.4s]" />
                <span className="text-sm text-foreground/70 ml-2">
                  AI đang suy nghĩ...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-foreground/10 bg-foreground/5">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Nhập câu hỏi của bạn..."
            className="flex-1 px-4 py-3 rounded-lg border border-foreground/20 bg-background text-foreground placeholder:text-foreground/50 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-all duration-200"
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl disabled:shadow-lg flex items-center gap-2"
            aria-label="Gửi tin nhắn">
            <IconSend size={18} />
            <span className="hidden sm:inline">Gửi</span>
          </button>
        </div>
      </div>
    </div>
  );
}
