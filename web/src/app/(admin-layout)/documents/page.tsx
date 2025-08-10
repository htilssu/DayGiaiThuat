import { Metadata } from "next";
import { Container, Paper, Title } from "@mantine/core";
import { DocumentUpload } from "@/components/DocumentUpload";

export const metadata: Metadata = {
  title: "Upload Documents - Admin Dashboard",
  description: "Quản lý và upload tài liệu cho hệ thống",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["admin", "documents", "upload", "tài liệu", "quản lý"],
};

export default function DocumentsPage() {
  return (
    <div>
      <Title order={2} className="mb-6">
        Upload Documents
      </Title>
      <Paper className="p-4 bg-white/50 border border-primary/10">
        <DocumentUpload />
      </Paper>
    </div>
  );
}
