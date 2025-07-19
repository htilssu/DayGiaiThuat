import { useEffect, useState, useRef } from "react";
import { IconSend } from "@tabler/icons-react";
import { TestResult } from "./types";
import { sendAIChatRequest } from "@/lib/api/aiChat";

export default function AIChat({
  code,
  results,
  calling,
  title,
  aiResponse,
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
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    // e.preventDefault();
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
    <div className="flex flex-col h-full border border-foreground/10 rounded-lg overflow-hidden theme-transition">
      {/* Header */}
      <div className="bg-foreground/5 p-3 border-b border-foreground/10">
        <h3 className="font-medium text-foreground">Tutor Agent</h3>
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-scroll p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}>
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === "user"
                  ? "bg-primary text-white"
                  : "bg-foreground/5 text-foreground border border-primary/30 shadow-sm"
              }`}>
              {message.role === "assistant"
                ? message.content.split("**").map((part, idx) => (
                    <span key={idx}>
                      {part}
                      {idx !== message.content.split("**").length - 1 && <br />}
                    </span>
                  ))
                : message.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-foreground/5 text-foreground rounded-lg px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 bg-foreground/40 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        // onSubmit={handleSubmit}
        className="p-4 border-t border-foreground/10">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Nhập câu hỏi của bạn..."
            className="flex-1 px-3 py-2 rounded-md border border-foreground/10 bg-background focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
          <button
            onClick={handleSubmit}
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Gửi tin nhắn">
            <IconSend size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
