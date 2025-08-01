'use client';

import React, { useState, useEffect } from 'react';
import { useWebSocket } from '@/contexts/WebSocketContext';
import { toast } from 'react-hot-toast';

interface NotificationData {
    title: string;
    message: string;
    type: 'info' | 'success' | 'warning' | 'error';
    duration?: number;
}

export const WebSocketNotification: React.FC = () => {
    const { lastMessage } = useWebSocket();
    const [notifications, setNotifications] = useState<NotificationData[]>([]);

    useEffect(() => {
        if (!lastMessage) return;

        const handleMessage = () => {
            switch (lastMessage.type) {
                case 'lesson_generation_status':
                    handleLessonGenerationStatus(lastMessage.data);
                    break;
                case 'document_processing_status':
                    handleDocumentProcessingStatus(lastMessage.data);
                    break;
                case 'notification':
                    handleNotification(lastMessage.data);
                    break;
                case 'error':
                    handleError(lastMessage.data);
                    break;
                default:
                    console.log('Received unknown message type:', lastMessage.type);
            }
        };

        handleMessage();
    }, [lastMessage]);

    const handleLessonGenerationStatus = (data: any) => {
        const { status, progress, message, topic_id } = data;

        switch (status) {
            case 'started':
                toast.success(`Bắt đầu tạo bài học cho chủ đề ${topic_id}`, {
                    duration: 3000,
                });
                break;
            case 'processing':
                toast.loading(`Đang tạo bài học... ${progress ? `${progress}%` : ''}`, {
                    id: `lesson-${topic_id}`,
                });
                break;
            case 'completed':
                toast.success(`Tạo bài học thành công cho chủ đề ${topic_id}`, {
                    id: `lesson-${topic_id}`,
                    duration: 5000,
                });
                break;
            case 'error':
                toast.error(`Lỗi tạo bài học: ${message}`, {
                    id: `lesson-${topic_id}`,
                    duration: 10000,
                });
                break;
        }
    };

    const handleDocumentProcessingStatus = (data: any) => {
        const { status, progress, message, filename } = data;

        switch (status) {
            case 'started':
                toast.success(`Bắt đầu xử lý tài liệu: ${filename}`, {
                    duration: 3000,
                });
                break;
            case 'processing':
                toast.loading(`Đang xử lý tài liệu... ${progress ? `${progress}%` : ''}`, {
                    id: `document-${filename}`,
                });
                break;
            case 'completed':
                toast.success(`Xử lý tài liệu thành công: ${filename}`, {
                    id: `document-${filename}`,
                    duration: 5000,
                });
                break;
            case 'error':
                toast.error(`Lỗi xử lý tài liệu: ${message}`, {
                    id: `document-${filename}`,
                    duration: 10000,
                });
                break;
        }
    };

    const handleNotification = (data: NotificationData) => {
        const { title, message, type, duration = 5000 } = data;
        const fullMessage = title ? `${title}: ${message}` : message;

        switch (type) {
            case 'success':
                toast.success(fullMessage, { duration });
                break;
            case 'error':
                toast.error(fullMessage, { duration });
                break;
            case 'warning':
                toast(fullMessage, {
                    icon: '⚠️',
                    duration
                });
                break;
            case 'info':
            default:
                toast(fullMessage, {
                    icon: 'ℹ️',
                    duration
                });
                break;
        }
    };

    const handleError = (data: any) => {
        const message = data.message || 'Đã xảy ra lỗi không xác định';
        toast.error(message, {
            duration: 10000,
        });
    };

    // Component này không render gì, chỉ xử lý thông báo
    return null;
};

export default WebSocketNotification; 