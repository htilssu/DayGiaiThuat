import { useState, useEffect, useCallback, DragEvent } from 'react';
import { notifications } from '@mantine/notifications';

export interface DragAndDropOptions {
    /** Các loại file được chấp nhận (mặc định: image/*) */
    acceptedTypes?: string[];
    /** Kích thước file tối đa (bytes, mặc định: 10MB) */
    maxFileSize?: number;
    /** Có cho phép nhiều file không (mặc định: false) */
    multiple?: boolean;
    /** Có hiển thị notification không (mặc định: true) */
    showNotifications?: boolean;
    /** Custom validation function */
    customValidator?: (file: File) => string | null;
}

export interface DragAndDropHandlers {
    onDragEnter: (e: DragEvent<HTMLElement>) => void;
    onDragLeave: (e: DragEvent<HTMLElement>) => void;
    onDragOver: (e: DragEvent<HTMLElement>) => void;
    onDrop: (e: DragEvent<HTMLElement>) => void;
}

export interface UseDragAndDropReturn {
    /** Trạng thái đang drag */
    isDragOver: boolean;
    /** Event handlers để bind vào element */
    dragHandlers: DragAndDropHandlers;
    /** Reset trạng thái drag */
    resetDragState: () => void;
}

const DEFAULT_OPTIONS: Required<DragAndDropOptions> = {
    acceptedTypes: ['image/*'],
    maxFileSize: 10 * 1024 * 1024, // 10MB
    multiple: false,
    showNotifications: true,
    customValidator: () => null,
};

export function useDragAndDrop(
    onFilesSelected: (files: File[]) => void,
    options: DragAndDropOptions = {},
    disabled: boolean = false
): UseDragAndDropReturn {
    const [isDragOver, setIsDragOver] = useState(false);

    const config = { ...DEFAULT_OPTIONS, ...options };

    // Validate file type
    const isValidFileType = useCallback((file: File): boolean => {
        return config.acceptedTypes.some(type => {
            if (type.endsWith('/*')) {
                const baseType = type.slice(0, -2);
                return file.type.startsWith(baseType);
            }
            return file.type === type;
        });
    }, [config.acceptedTypes]);

    // Validate file size
    const isValidFileSize = useCallback((file: File): boolean => {
        return file.size <= config.maxFileSize;
    }, [config.maxFileSize]);

    // Validate files
    const validateFiles = useCallback((files: File[]): { valid: File[]; errors: string[] } => {
        const valid: File[] = [];
        const errors: string[] = [];

        for (const file of files) {
            // Check file type
            if (!isValidFileType(file)) {
                errors.push(`File "${file.name}" có định dạng không được hỗ trợ.`);
                continue;
            }

            // Check file size
            if (!isValidFileSize(file)) {
                const maxSizeMB = (config.maxFileSize / (1024 * 1024)).toFixed(1);
                errors.push(`File "${file.name}" quá lớn. Kích thước tối đa: ${maxSizeMB}MB.`);
                continue;
            }

            // Custom validation
            const customError = config.customValidator(file);
            if (customError) {
                errors.push(customError);
                continue;
            }

            valid.push(file);
        }

        return { valid, errors };
    }, [isValidFileType, isValidFileSize, config.customValidator]);

    // Format accepted types for user display
    const getAcceptedTypesText = useCallback((): string => {
        const types = config.acceptedTypes.map(type => {
            if (type === 'image/*') return 'Ảnh (JPG, PNG, GIF)';
            if (type === 'video/*') return 'Video';
            if (type === 'audio/*') return 'Audio';
            if (type === 'application/pdf') return 'PDF';
            return type.split('/')[1]?.toUpperCase() || type;
        });
        return types.join(', ');
    }, [config.acceptedTypes]);

    // Drag event handlers
    const handleDragEnter = useCallback((e: DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
        if (!disabled) {
            setIsDragOver(true);
        }
    }, [disabled]);

    const handleDragLeave = useCallback((e: DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
        if (!disabled) {
            setIsDragOver(false);
        }
    }, [disabled]);

    const handleDragOver = useCallback((e: DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
    }, []);

    const handleDrop = useCallback((e: DragEvent<HTMLElement>) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragOver(false);

        if (disabled) return;

        const files = Array.from(e.dataTransfer.files);

        if (files.length === 0) {
            if (config.showNotifications) {
                notifications.show({
                    title: 'Lỗi',
                    message: 'Không có file nào được kéo thả.',
                    color: 'red',
                });
            }
            return;
        }

        // Limit files if not multiple
        const filesToProcess = config.multiple ? files : files.slice(0, 1);

        const { valid, errors } = validateFiles(filesToProcess);

        // Show validation errors
        if (errors.length > 0 && config.showNotifications) {
            errors.forEach(error => {
                notifications.show({
                    title: 'Lỗi validation',
                    message: error,
                    color: 'red',
                });
            });
        }

        // Process valid files
        if (valid.length > 0) {
            onFilesSelected(valid);

            if (config.showNotifications) {
                const fileNames = valid.map(f => f.name).join(', ');
                notifications.show({
                    title: 'Thành công',
                    message: `Đã chọn file: ${fileNames}`,
                    color: 'green',
                });
            }
        }
    }, [disabled, config, validateFiles, onFilesSelected]);

    // Reset drag state
    const resetDragState = useCallback(() => {
        setIsDragOver(false);
    }, []);

    // Global drag prevention effect
    useEffect(() => {
        const handleGlobalDragOver = (e: Event) => {
            e.preventDefault();
        };

        const handleGlobalDrop = (e: Event) => {
            e.preventDefault();
        };

        // Prevent default browser drag behavior
        document.addEventListener('dragover', handleGlobalDragOver);
        document.addEventListener('drop', handleGlobalDrop);

        return () => {
            document.removeEventListener('dragover', handleGlobalDragOver);
            document.removeEventListener('drop', handleGlobalDrop);
        };
    }, []);

    return {
        isDragOver,
        dragHandlers: {
            onDragEnter: handleDragEnter,
            onDragLeave: handleDragLeave,
            onDragOver: handleDragOver,
            onDrop: handleDrop,
        },
        resetDragState,
    };
} 