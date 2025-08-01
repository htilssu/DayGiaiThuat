"use client";

import { useEffect, useState } from "react";
import {
  Text,
  Group,
  Stack,
  Button,
  Paper,
  useMantineTheme,
} from "@mantine/core";
import { Dropzone, FileWithPath } from "@mantine/dropzone";
import { IconCloudUpload, IconX, IconFile } from "@tabler/icons-react";
import { Document } from "@/lib/api/documents";
import { DocumentStatus } from "./DocumentStatus";
import { documentsApi } from "@/lib/api";
import { notifications } from "@mantine/notifications";

export function DocumentUpload() {
  const theme = useMantineTheme();
  const [files, setFiles] = useState<FileWithPath[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    const pollStatus = async () => {
      const processingDocs = documents.filter(
        (doc) => doc.status === "processing"
      );
      if (processingDocs.length > 0) {
        try {
          const updatedDocs = await documentsApi.getStatus(
            processingDocs.map((doc) => doc.id)
          );
          setDocuments((prev) =>
            prev.map((doc) => {
              const updated = updatedDocs.find((u) => u.id === doc.id);
              return updated || doc;
            })
          );
        } catch (error) {
          console.error("Error polling status:", error);
        }
      }
    };

    const interval = setInterval(pollStatus, 5000);
    return () => clearInterval(interval);
  }, [documents]);

  const handleDrop = (droppedFiles: FileWithPath[]) => {
    setFiles((prev) => [...prev, ...droppedFiles]);
  };

  const handleUpload = async () => {
    if (files.length === 0) return;

    setIsUploading(true);
    try {
      const response = await documentsApi.upload(files);
      setDocuments((prev) => [...prev, ...response.documents]);
      setFiles([]);
      notifications.show({
        title: "Success",
        message: "Documents uploaded successfully",
        color: "teal",
      });
    } catch (error) {
      console.error("Error uploading documents:", error);
      notifications.show({
        title: "Error",
        message: "Failed to upload documents",
        color: "red",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <Stack gap="md">
      <Dropzone
        onDrop={handleDrop}
        onReject={() => {
          notifications.show({
            title: "Error",
            message: "Some files were rejected",
            color: "red",
          });
        }}
        // maxSize={5 * 1024 ** 2} // 5MB
        accept={["application/pdf", "text/plain", ".doc", ".docx"]}
        className="bg-white/50 border-primary/20 hover:border-primary/40 transition-colors">
        <Group
          justify="center"
          gap="xl"
          style={{ minHeight: 220, pointerEvents: "none" }}>
          <Dropzone.Accept>
            <IconCloudUpload
              size="3.2rem"
              stroke={1.5}
              className="text-primary"
            />
          </Dropzone.Accept>
          <Dropzone.Reject>
            <IconX size="3.2rem" stroke={1.5} color={theme.colors.red[6]} />
          </Dropzone.Reject>
          <Dropzone.Idle>
            <IconCloudUpload
              size="3.2rem"
              stroke={1.5}
              className="text-primary/70"
            />
          </Dropzone.Idle>

          <div>
            <Text size="xl" inline className="text-primary">
              Drag documents here or click to select files
            </Text>
            <Text size="sm" className="text-primary/60" inline mt={7}>
              Upload PDF, TXT, DOC, or DOCX files (max 5MB each)
            </Text>
          </div>
        </Group>
      </Dropzone>

      {files.length > 0 && (
        <Paper className="border border-primary/10 bg-white/50" p="md">
          <Stack gap="xs">
            <Text fw={500} className="text-primary">
              Selected Files:
            </Text>
            {files.map((file, index) => (
              <Group key={index} justify="apart">
                <Group gap="xs">
                  <IconFile size="1.2rem" className="text-primary/70" />
                  <Text size="sm" className="text-primary/80">
                    {file.name}
                  </Text>
                </Group>
                <Button
                  variant="subtle"
                  color="red"
                  size="xs"
                  onClick={() => removeFile(index)}
                  className="hover:bg-red-50">
                  Remove
                </Button>
              </Group>
            ))}
            <Button
              onClick={handleUpload}
              loading={isUploading}
              disabled={files.length === 0}
              mt="sm"
              className="bg-primary hover:bg-primary/90 text-white transition-colors">
              Upload {files.length} file(s)
            </Button>
          </Stack>
        </Paper>
      )}

      {documents.length > 0 && (
        <Stack gap="xs">
          <Text fw={500} className="text-primary">
            Processed Documents:
          </Text>
          {documents.map((doc) => (
            <DocumentStatus key={doc.id} document={doc} />
          ))}
        </Stack>
      )}
    </Stack>
  );
}
