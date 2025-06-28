"use client";

import { AdminChat } from "@/components/Chat";
import { DocumentUpload } from "@/components/DocumentUpload";
import { Container, Grid, Paper, Title } from "@mantine/core";

export default function AIRequestPage() {
  return (
    <div className="space-y-8">
      <Paper className="p-6 bg-primary/5 rounded-lg border border-primary/10">
        <Title order={2} className="mb-6 text-gradient-theme">
          AI Content Creator
        </Title>
        <Grid>
          <Grid.Col span={7}>
            <Paper className="p-4 bg-white/50 border border-primary/10">
              <AdminChat />
            </Paper>
          </Grid.Col>
          <Grid.Col span={5}>
            <Paper className="p-4 bg-white/50 border border-primary/10">
              <DocumentUpload />
            </Paper>
          </Grid.Col>
        </Grid>
      </Paper>
    </div>
  );
}
