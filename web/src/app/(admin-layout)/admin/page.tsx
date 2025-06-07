"use client";

import { useState } from "react";
import { Chat } from "@/components/Chat";
import { Container, Title } from "@mantine/core";
import Overview from "@/components/admin/Overview";

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4 text-gray-800">
          Admin Dashboard
        </h1>
        <div className="flex space-x-4">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
              activeTab === "overview"
                ? "bg-primary text-white"
                : "bg-white text-gray-600 hover:bg-gray-100"
            }`}>
            Overview
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
              activeTab === "users"
                ? "bg-primary text-white"
                : "bg-white text-gray-600 hover:bg-gray-100"
            }`}>
            Users
          </button>
          <button
            onClick={() => setActiveTab("chat")}
            className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
              activeTab === "chat"
                ? "bg-primary text-white"
                : "bg-white text-gray-600 hover:bg-gray-100"
            }`}>
            Chat
          </button>
          <button
            onClick={() => setActiveTab("add-documents")}
            className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
              activeTab === "add-documents"
                ? "bg-primary text-white"
                : "bg-white text-gray-600 hover:bg-gray-100"
            }`}>
            Add documents
          </button>
        </div>
      </div>

      {activeTab === "overview" && <Overview />}
      {activeTab === "chat" && (
        <Container size="lg" py="xl">
          <Title order={2} mb="xl">
            AI Assistant
          </Title>
          <Chat />
        </Container>
      )}
    </div>
  );
}
