import { Box, Button, Group, Text } from "@mantine/core";
import {
  IconBook,
  IconFileText,
  IconBrain,
  IconQuestionMark,
} from "@tabler/icons-react";
import { ContentType, ContentOption } from "./types";

interface ContentOptionsProps {
  onContentTypeSelect: (type: ContentType) => void;
}

const contentOptions: ContentOption[] = [
  {
    type: "topic",
    icon: IconBook,
    label: "Create Topic",
    description: "Create a new topic for a course",
    color: "blue",
  },
  {
    type: "lesson",
    icon: IconFileText,
    label: "Create Lesson",
    description: "Generate a new lesson with AI",
    color: "green",
  },
  {
    type: "exercise",
    icon: IconBrain,
    label: "Create Exercise",
    description: "Create a new exercise",
    color: "orange",
  },
  {
    type: "quiz",
    icon: IconQuestionMark,
    label: "Create Quiz",
    description: "Create a new quiz",
    color: "purple",
  },
];

export function ContentOptions({ onContentTypeSelect }: ContentOptionsProps) {
  return (
    <Box mb="md">
      <Text size="sm" fw={500} mb="xs" c="dimmed">
        Create Content with AI
      </Text>
      <Group gap="xs">
        {contentOptions.map((option) => (
          <Button
            key={option.type}
            variant="light"
            size="xs"
            leftSection={<option.icon size={16} />}
            onClick={() => onContentTypeSelect(option.type)}
            color={option.color}
            style={{ flex: 1 }}>
            {option.label}
          </Button>
        ))}
      </Group>
    </Box>
  );
}
