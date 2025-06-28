import React, { useState } from 'react';
import { Stack, Title, Text, Paper, Group, Badge, Button } from '@mantine/core';
import { IconPhoto, IconFile, IconTrash } from '@tabler/icons-react';
import { DragDropZone } from './DragDropZone';
import { useDragAndDrop } from '@/hooks/useDragAndDrop';

export function DragDropDemo() {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

    // Example 1: Basic image upload
    const handleImageFiles = (files: File[]) => {
        setSelectedFiles(prev => [...prev, ...files]);
    };

    // Example 2: Using hook directly
    const { isDragOver: isDragOver2, dragHandlers: dragHandlers2 } = useDragAndDrop(
        (files) => {
            console.log('Files from hook:', files);
            setSelectedFiles(prev => [...prev, ...files]);
        },
        {
            acceptedTypes: ['application/pdf', 'image/*'],
            maxFileSize: 5 * 1024 * 1024, // 5MB
            multiple: true,
        }
    );

    const clearFiles = () => setSelectedFiles([]);

    const formatFileSize = (bytes: number) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <Title order={2} mb="xl">🎯 Drag & Drop Components Demo</Title>

            <Stack gap="xl">
                {/* Example 1: Simple Image Upload */}
                <Paper p="md" shadow="sm">
                    <Title order={4} mb="md">📸 Example 1: Simple Image Upload</Title>
                    <DragDropZone
                        onFilesSelected={handleImageFiles}
                        acceptedTypes={['image/*']}
                        maxFileSize={10 * 1024 * 1024}
                        height={150}
                        primaryText="Kéo thả ảnh vào đây"
                        secondaryText="JPG, PNG, GIF tối đa 10MB"
                        dragText="Thả ảnh ngay đây!"
                    />
                </Paper>

                {/* Example 2: Multiple File Types with Custom Styling */}
                <Paper p="md" shadow="sm">
                    <Title order={4} mb="md">📄 Example 2: Multiple File Types</Title>
                    <DragDropZone
                        onFilesSelected={handleImageFiles}
                        acceptedTypes={['image/*', 'application/pdf', 'text/*']}
                        maxFileSize={5 * 1024 * 1024}
                        multiple={true}
                        height={120}
                        icon={<IconFile size={40} />}
                        primaryText="Upload documents & images"
                        secondaryText="PDF, Images, Text files up to 5MB"
                        className="border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-400"
                    />
                </Paper>

                {/* Example 3: With Existing Image */}
                <Paper p="md" shadow="sm">
                    <Title order={4} mb="md">🖼️ Example 3: Replace Existing Image</Title>
                    <DragDropZone
                        onFilesSelected={handleImageFiles}
                        acceptedTypes={['image/*']}
                        height={200}
                        dragText="Thả ảnh mới để thay thế"
                    >
                        <img
                            src="/images/placeholder-course.jpg"
                            alt="Current image"
                            className="w-full h-full object-cover rounded-md"
                        />
                    </DragDropZone>
                </Paper>

                {/* Example 4: Using Hook Directly */}
                <Paper p="md" shadow="sm">
                    <Title order={4} mb="md">🔧 Example 4: Using Hook Directly</Title>
                    <div
                        {...dragHandlers2}
                        className={`
              p-8 border-2 border-dashed rounded-lg text-center transition-all
              ${isDragOver2
                                ? 'border-blue-500 bg-blue-50 scale-105'
                                : 'border-gray-300 hover:border-gray-400'
                            }
            `}
                    >
                        <Text size="lg" fw={500}>
                            {isDragOver2 ? '📥 Drop files here!' : '📎 Custom styled drop zone'}
                        </Text>
                        <Text size="sm" c="dimmed">
                            PDF, Images • Max 5MB • Multiple files
                        </Text>
                    </div>
                </Paper>

                {/* Selected Files Display */}
                {selectedFiles.length > 0 && (
                    <Paper p="md" shadow="sm">
                        <Group justify="space-between" mb="md">
                            <Title order={4}>📋 Selected Files ({selectedFiles.length})</Title>
                            <Button
                                variant="outline"
                                color="red"
                                size="sm"
                                leftSection={<IconTrash size={16} />}
                                onClick={clearFiles}
                            >
                                Clear All
                            </Button>
                        </Group>

                        <Stack gap="xs">
                            {selectedFiles.map((file, index) => (
                                <Group key={index} justify="space-between" className="p-2 bg-gray-50 rounded">
                                    <Group gap="xs">
                                        {file.type.startsWith('image/') ? (
                                            <IconPhoto size={20} className="text-blue-500" />
                                        ) : (
                                            <IconFile size={20} className="text-gray-500" />
                                        )}
                                        <div>
                                            <Text size="sm" fw={500}>{file.name}</Text>
                                            <Text size="xs" c="dimmed">{file.type}</Text>
                                        </div>
                                    </Group>
                                    <Badge variant="light" size="sm">
                                        {formatFileSize(file.size)}
                                    </Badge>
                                </Group>
                            ))}
                        </Stack>
                    </Paper>
                )}

                {/* Usage Instructions */}
                <Paper p="md" shadow="sm" className="bg-blue-50">
                    <Title order={4} mb="md">💡 Usage Instructions</Title>
                    <Stack gap="xs">
                        <Text size="sm">
                            <strong>Hook Usage:</strong> <code>useDragAndDrop(onFilesSelected, options, disabled)</code>
                        </Text>
                        <Text size="sm">
                            <strong>Component Usage:</strong> <code>{'<DragDropZone onFilesSelected={handleFiles} />'}</code>
                        </Text>
                        <Text size="sm">
                            <strong>Features:</strong> File validation, size limits, type filtering, multiple files, custom styling
                        </Text>
                    </Stack>
                </Paper>
            </Stack>
        </div>
    );
}

export default DragDropDemo; 