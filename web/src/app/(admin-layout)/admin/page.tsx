"use client";

import { useState } from "react";
import { AdminChat } from "@/components/Chat";
import { Container, Paper, Tabs, Title } from "@mantine/core";
import Overview from "@/components/admin/Overview";
import { DocumentUpload } from "@/components/DocumentUpload";
import {
  IconChartBar,
  IconMessage,
  IconUpload,
  IconUsers,
} from "@tabler/icons-react";

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="space-y-8">
      <Paper className="p-6 bg-primary/5 rounded-lg border border-primary/10">
        <Tabs
          value={activeTab}
          onChange={(value) => setActiveTab(value || "overview")}
          variant="outline"
          classNames={{
            tab: "text-lg text-primary text-shadow-sm data-[active]:bg-primary data-[active]:text-white hover:bg-primary/10 transition-colors duration-200",
            panel: "mt-6",
          }}>
          <Tabs.List>
            <Tabs.Tab
              value="overview"
              leftSection={<IconChartBar size={16} />}
              className="font-medium">
              Overview
            </Tabs.Tab>
            <Tabs.Tab
              value="users"
              leftSection={<IconUsers size={16} />}
              className="font-medium">
              Users
            </Tabs.Tab>
            <Tabs.Tab
              value="chat"
              leftSection={<IconMessage size={16} />}
              className="font-medium">
              AI Assistant
            </Tabs.Tab>
            <Tabs.Tab
              value="add-documents"
              leftSection={<IconUpload size={16} />}
              className="font-medium">
              Add Documents
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="overview">
            <Overview />
          </Tabs.Panel>

          <Tabs.Panel value="chat">
            <Container size="lg" className="px-0">
              <Title order={2} className="mb-6">
                AI Content Creator
              </Title>
              <Paper className="p-4 bg-white/50 border border-primary/10">
                <AdminChat />
              </Paper>
            </Container>
          </Tabs.Panel>

          <Tabs.Panel value="add-documents">
            <Container size="lg" className="px-0">
              <Title order={2} className="mb-6 ">
                Upload Documents
              </Title>
              <Paper className="p-4 bg-white/50 border border-primary/10">
                <DocumentUpload />
              </Paper>
            </Container>
          </Tabs.Panel>
        </Tabs>
      </Paper>
    </div>
  );
}
