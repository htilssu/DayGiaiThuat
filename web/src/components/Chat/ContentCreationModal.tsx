import { Modal, Box, Group, Text, Button } from "@mantine/core";
import { IconPlus, IconX } from "@tabler/icons-react";
import { ContentType, ContentFormData } from "./types";
import { ContentForm } from "./ContentForm";

interface ContentCreationModalProps {
  opened: boolean;
  onClose: () => void;
  contentType: ContentType | null;
  formData: ContentFormData;
  onFormDataChange: (formData: ContentFormData) => void;
  onCreateContent: () => void;
  isLoading: boolean;
}

export function ContentCreationModal({
  opened,
  onClose,
  contentType,
  formData,
  onFormDataChange,
  onCreateContent,
  isLoading,
}: ContentCreationModalProps) {
  if (!contentType) return null;

  const getContentIcon = () => {
    switch (contentType) {
      case "topic":
        return "📚";
      case "lesson":
        return "📄";
      case "exercise":
        return "🧠";
      case "quiz":
        return "❓";
      default:
        return null;
    }
  };

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group>
          <Text>{getContentIcon()}</Text>
          <Text>
            Create {contentType.charAt(0).toUpperCase() + contentType.slice(1)}
          </Text>
        </Group>
      }
      size="lg"
      closeOnClickOutside={false}>
      <Box>
        <ContentForm
          contentType={contentType}
          formData={formData}
          onFormDataChange={onFormDataChange}
        />
        <Group justify="flex-end" mt="xl">
          <Button
            variant="light"
            color="teal"
            onClick={onClose}
            leftSection={<IconX size={16} />}>
            Cancel
          </Button>
          <Button
            color="teal"
            onClick={onCreateContent}
            leftSection={<IconPlus size={16} />}
            loading={isLoading}>
            Create {contentType.charAt(0).toUpperCase() + contentType.slice(1)}
          </Button>
        </Group>
      </Box>
    </Modal>
  );
}
