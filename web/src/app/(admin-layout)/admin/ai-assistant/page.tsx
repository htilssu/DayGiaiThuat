import { Metadata } from "next";
import { Container, Paper, Title } from "@mantine/core";
import { AdminChat } from "@/components/Chat";

export const metadata: Metadata = {
  title: "AI Assistant - Admin Dashboard",
  description: "Trợ lý AI cho quản trị viên",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["admin", "AI", "assistant", "chat", "trợ lý"],
};

export default function AIAssistantPage() {
  return (
    <div>
      <Title order={2} className="mb-6">
        AI Content Creator
      </Title>
      <Paper className="p-4 bg-white/50 border border-primary/10">
        <AdminChat />
      </Paper>
    </div>
  );
}
