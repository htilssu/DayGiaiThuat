import React, { ReactNode } from 'react';
import { Box, Text } from '@mantine/core';
import { IconPhoto, IconUpload, IconFile } from '@tabler/icons-react';
import { useDragAndDrop, DragAndDropOptions } from '@/hooks/useDragAndDrop';

interface DragDropZoneProps extends DragAndDropOptions {
    /** Function được gọi khi files được chọn */
    onFilesSelected: (files: File[]) => void;
    /** Component children để render bên trong zone */
    children?: ReactNode;
    /** Custom placeholder khi không có children */
    placeholder?: ReactNode;
    /** Custom overlay khi đang drag */
    dragOverlay?: ReactNode;
    /** Disabled state */
    disabled?: boolean;
    /** Custom className */
    className?: string;
    /** Custom style */
    style?: React.CSSProperties;
    /** Chiều cao của zone (mặc định: auto) */
    height?: string | number;
    /** Icon hiển thị (mặc định: photo cho image, file cho khác) */
    icon?: ReactNode;
    /** Text chính */
    primaryText?: string;
    /** Text phụ */
    secondaryText?: string;
    /** Text khi đang drag */
    dragText?: string;
}

export function DragDropZone({
    onFilesSelected,
    children,
    placeholder,
    dragOverlay,
    disabled = false,
    className = '',
    style,
    height = 'auto',
    icon,
    primaryText,
    secondaryText,
    dragText,
    ...dragOptions
}: DragDropZoneProps) {
    const { isDragOver, dragHandlers } = useDragAndDrop(
        onFilesSelected,
        dragOptions,
        disabled
    );

    // Determine default icon based on accepted types
    const getDefaultIcon = () => {
        if (icon) return icon;

        const acceptedTypes = dragOptions.acceptedTypes || ['image/*'];
        if (acceptedTypes.some(type => type.startsWith('image'))) {
            return <IconPhoto size={48} />;
        }
        return <IconFile size={48} />;
    };

    // Get file type text
    const getFileTypeText = () => {
        const acceptedTypes = dragOptions.acceptedTypes || ['image/*'];
        const maxSizeMB = ((dragOptions.maxFileSize || 10 * 1024 * 1024) / (1024 * 1024)).toFixed(1);

        let typeText = 'File';
        if (acceptedTypes.some(type => type.startsWith('image'))) {
            typeText = 'JPG, PNG, GIF';
        } else if (acceptedTypes.some(type => type.startsWith('video'))) {
            typeText = 'Video';
        } else if (acceptedTypes.some(type => type.startsWith('audio'))) {
            typeText = 'Audio';
        }

        return `${typeText} tối đa ${maxSizeMB}MB`;
    };

    // Default placeholder content
    const defaultPlaceholder = (
        <Box className="text-center">
            <Box className={`mx-auto mb-2 ${isDragOver ? 'text-blue-500' : 'text-gray-400'}`}>
                {getDefaultIcon()}
            </Box>
            <Text
                size="sm"
                c={isDragOver ? 'blue' : 'dimmed'}
                fw={isDragOver ? 500 : 400}
            >
                {isDragOver
                    ? (dragText || 'Thả file vào đây')
                    : (primaryText || 'Nhấn hoặc kéo thả file vào đây')
                }
            </Text>
            <Text size="xs" c={isDragOver ? 'blue' : 'dimmed'}>
                {secondaryText || getFileTypeText()}
            </Text>
        </Box>
    );

    // Default drag overlay
    const defaultDragOverlay = dragOverlay || (
        <Box
            style={{
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: 'rgba(59, 130, 246, 0.9)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 10,
            }}
        >
            <Box className="text-center text-white">
                <Box className="mx-auto mb-2">
                    <IconUpload size={48} color="white" />
                </Box>
                <Text size="lg" fw={600} style={{ color: 'white' }}>
                    {dragText || 'Thả file vào đây'}
                </Text>
                <Text size="sm" style={{ color: 'white', opacity: 0.9 }}>
                    Để upload file
                </Text>
            </Box>
        </Box>
    );

    return (
        <Box
            className={`
        relative transition-all duration-200 cursor-pointer
        ${isDragOver
                    ? 'transform scale-105'
                    : ''
                }
        ${disabled
                    ? 'cursor-not-allowed opacity-50'
                    : 'hover:shadow-md'
                }
        ${className}
      `}
            style={{
                height,
                minHeight: children ? 'auto' : '120px',
                ...style
            }}
            {...(disabled ? {} : dragHandlers)}
        >
            {/* Main content */}
            {children ? (
                <Box className={`transition-all duration-200 ${isDragOver ? 'opacity-70' : ''}`}>
                    {children}
                </Box>
            ) : (
                <Box
                    className={`
            w-full h-full rounded-md flex items-center justify-center transition-all duration-200
            ${isDragOver
                            ? 'bg-blue-50 border-2 border-dashed border-blue-400'
                            : 'bg-gray-100 border-2 border-dashed border-gray-300 hover:bg-gray-50 hover:border-gray-400'
                        }
          `}
                >
                    {placeholder || defaultPlaceholder}
                </Box>
            )}

            {/* Drag overlay */}
            {isDragOver && children && defaultDragOverlay}
        </Box>
    );
}

export default DragDropZone; 