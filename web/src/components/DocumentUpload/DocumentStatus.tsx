import { Badge, Group, Paper, Text, ThemeIcon } from "@mantine/core";
import { IconCheck, IconClock, IconX, IconFileText } from "@tabler/icons-react";
import { Document } from "@/lib/api/documents";

interface DocumentStatusProps {
  document: Document;
}

export function DocumentStatus({ document }: DocumentStatusProps) {
  const getStatusColor = () => {
    switch (document.status) {
      case "completed":
        return "bg-primary/20 text-primary border-primary/20";
      case "processing":
        return "bg-secondary/20 text-secondary border-secondary/20";
      case "failed":
        return "bg-red-100 text-red-700 border-red-200";
      default:
        return "bg-secondary/20 text-secondary border-secondary/20";
    }
  };

  const getStatusIcon = () => {
    switch (document.status) {
      case "completed":
        return <IconCheck size="1rem" />;
      case "processing":
        return <IconClock size="1rem" />;
      case "failed":
        return <IconX size="1rem" />;
      default:
        return <IconFileText size="1rem" />;
    }
  };

  const getIconColor = () => {
    switch (document.status) {
      case "completed":
        return "text-primary bg-primary/20";
      case "processing":
        return "text-secondary bg-secondary/20";
      case "failed":
        return "text-red-700 bg-red-100";
      default:
        return "text-secondary bg-secondary/20";
    }
  };

  return (
    <Paper className="border border-primary/10 bg-white/50 rounded-lg" p="md">
      <Group position="apart">
        <Group>
          <ThemeIcon className={getIconColor()} size="lg" radius="xl">
            {getStatusIcon()}
          </ThemeIcon>
          <div>
            <Text className="text-primary/90 font-medium" size="sm">
              {document.filename}
            </Text>
            <Text className="text-primary/60" size="xs">
              {new Date(document.createdAt).toLocaleString()}
            </Text>
          </div>
        </Group>
        <Badge className={getStatusColor()}>
          {document.status.charAt(0).toUpperCase() + document.status.slice(1)}
        </Badge>
      </Group>
      {document.error && (
        <Text className="text-red-600 mt-2" size="xs">
          Error: {document.error}
        </Text>
      )}
    </Paper>
  );
}
