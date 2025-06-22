import { Metadata } from "next";
import { DocumentManager } from "@/components/DocumentUpload";

export const metadata: Metadata = {
  title: "Document Management - Vector Database",
  description:
    "Upload and search documents in the vector database for AI-powered retrieval",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["documents", "vector database", "AI", "search", "upload"],
};

export default function DocumentsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-primary mb-2">
            Document Management
          </h1>
          <p className="text-primary/70">
            Upload documents to the vector database and search through them
            using AI-powered semantic search.
          </p>
        </div>

        <DocumentManager />
      </div>
    </div>
  );
}
