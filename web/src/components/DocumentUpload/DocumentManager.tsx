"use client";

import { useState } from "react";
import { Tabs, TabsList, TabsTab, TabsPanel, Stack } from "@mantine/core";
import { IconUpload, IconSearch } from "@tabler/icons-react";
import { DocumentUpload } from "./DocumentUpload";
import { DocumentSearch } from "./DocumentSearch";

export function DocumentManager() {
  const [activeTab, setActiveTab] = useState<string | null>("upload");

  return (
    <Stack gap="lg">
      <Tabs value={activeTab} onChange={setActiveTab}>
        <TabsList className="bg-white/50 border border-primary/10">
          <TabsTab
            value="upload"
            leftSection={<IconUpload size="1rem" />}
            className="text-primary data-[active]:bg-primary data-[active]:text-white">
            Upload Documents
          </TabsTab>
          <TabsTab
            value="search"
            leftSection={<IconSearch size="1rem" />}
            className="text-primary data-[active]:bg-primary data-[active]:text-white">
            Search Documents
          </TabsTab>
        </TabsList>

        <TabsPanel value="upload" pt="md">
          <DocumentUpload />
        </TabsPanel>

        <TabsPanel value="search" pt="md">
          <DocumentSearch />
        </TabsPanel>
      </Tabs>
    </Stack>
  );
}
