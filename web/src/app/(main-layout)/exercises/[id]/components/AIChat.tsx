import { useEffect, useState, useRef } from "react";
import { IconSend } from "@tabler/icons-react";
import { GoogleGenAI } from "@google/genai";
import { TestResult } from "./types";

export default function AIChat({
  code,
  results,
  calling,
  title,
}: {
  code: string;
  results: TestResult[];
  calling: {
    callAIChat: boolean;
    setCallAIChat: (value: boolean) => void;
  };
  title: string;
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

  const ai = new GoogleGenAI({
    apiKey: "AIzaSyAoWvIFmtiL1MwP1y8ariEm61Zaq4-uNZo",
  });

  const handleTest = async () => {
    setIsLoading(true);
    try {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-05-20",
        contents: `Đây là code của học viên: ${code} và đây là kết quả test: ${results}. Đây là tiêu đề bài tập: ${title}`,
        config: {
          systemInstruction: `Bạn là một chuyên gia giải thuật chuyên nghiệp, dễ thương và thân thiện. Nhiệm vụ của bạn là đưa ra gợi ý cho học viên nếu họ làm bài chưa đúng và khen họ nếu họ đã đúng. Hãy đưa ra gợi ý thật ngắn gọn, dễ hiểu và có chút chăm chọc. Hãy chỉ đưa ra gợi ý về cách giải, không đưa ra lời giải cụ thể.`,
        },
      });

      if (response.text) {
        const aiMessage: { role: "assistant"; content: string } = {
          role: "assistant",
          content: response.text,
        };
        setMessages((prev) => [...prev, aiMessage]);
      }
      calling.setCallAIChat(false);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-05-20",
        contents: input,
        config: {
          systemInstruction:
            "Bạn là một giảng viên dạy thuật toán chuyên nghiệp và thân thiện. Nhiệm vụ của bạn là giao tiếp và hỗ trợ giải đáp thắc mắc của học viên. Hãy trả lời 1 cách ngắn gọn và súc tích.",
        },
      });

      if (response.text) {
        const aiMessage: { role: "assistant"; content: string } = {
          role: "assistant",
          content: response.text,
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
      handleTest();
    }
  }, [calling.callAIChat]);

  return (
    <div className="flex flex-col h-full border border-foreground/10 rounded-lg overflow-hidden theme-transition">
      {/* Header */}
      <div className="bg-foreground/5 p-3 border-b border-foreground/10">
        <h3 className="font-medium text-foreground">Tutor Agent</h3>
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
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === "user"
                  ? "bg-primary text-white"
                  : "bg-foreground/5 text-foreground"
              }`}>
              {message.content}
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
            onClick={handleTest}
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
