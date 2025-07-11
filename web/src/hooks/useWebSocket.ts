import { useContext, useEffect, useCallback } from 'react';
import WebSocketContext from '@/contexts/WebSocketContext';

interface WebSocketMessage {
    type: string;
    data: any;
    timestamp?: string;
}

export const useWebSocketMessage = (
    messageType: string,
    callback: (data: any) => void
) => {
    const context = useContext(WebSocketContext);

    if (!context) {
        throw new Error('useWebSocketMessage phải được sử dụng trong WebSocketProvider');
    }

    const { lastMessage } = context;

    useEffect(() => {
        if (lastMessage && lastMessage.type === messageType) {
            callback(lastMessage.data);
        }
    }, [lastMessage, messageType, callback]);

    return context;
};

export const useWebSocketSender = () => {
    const context = useContext(WebSocketContext);

    if (!context) {
        throw new Error('useWebSocketSender phải được sử dụng trong WebSocketProvider');
    }

    const { sendMessage, isConnected } = context;

    const sendMessageSafe = useCallback((message: WebSocketMessage) => {
        if (isConnected) {
            sendMessage(message);
            return true;
        } else {
            console.warn('WebSocket chưa kết nối, không thể gửi tin nhắn');
            return false;
        }
    }, [sendMessage, isConnected]);

    return {
        sendMessage: sendMessageSafe,
        isConnected
    };
};

// Hook để lắng nghe trạng thái tạo bài học
export const useLessonGenerationStatus = (callback: (status: any) => void) => {
    return useWebSocketMessage('lesson_generation_status', callback);
};

// Hook để lắng nghe trạng thái xử lý tài liệu
export const useDocumentProcessingStatus = (callback: (status: any) => void) => {
    return useWebSocketMessage('document_processing_status', callback);
};

// Hook để lắng nghe thông báo chung
export const useNotification = (callback: (notification: any) => void) => {
    return useWebSocketMessage('notification', callback);
};

export default useWebSocketMessage; 