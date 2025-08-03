'use client';

import React, { useState } from 'react';
import {
    useLessonGenerationStatus,
    useDocumentProcessingStatus,
    useNotification,
    useWebSocketSender
} from '@/hooks';
import { useWebSocket } from '@/contexts/WebSocketContext';
import WebSocketStatus from '@/components/ui/WebSocketStatus';

/**
 * Component ví dụ về cách sử dụng WebSocket
 */
export const WebSocketExample: React.FC = () => {
    const [messages, setMessages] = useState<string[]>([]);
    const { isConnected, connectionStatus } = useWebSocket();
    const { sendMessage } = useWebSocketSender();

    // Lắng nghe trạng thái tạo bài học
    useLessonGenerationStatus((status) => {
        setMessages(prev => [...prev, `Lesson Generation: ${JSON.stringify(status)}`]);
    });

    // Lắng nghe trạng thái xử lý tài liệu
    useDocumentProcessingStatus((status) => {
        setMessages(prev => [...prev, `Document Processing: ${JSON.stringify(status)}`]);
    });

    // Lắng nghe thông báo chung
    useNotification((notification) => {
        setMessages(prev => [...prev, `Notification: ${JSON.stringify(notification)}`]);
    });

    const handleSendTestMessage = () => {
        const success = sendMessage({
            type: 'test_message',
            data: {
                content: 'Test message from client',
                timestamp: Date.now()
            }
        });

        if (success) {
            setMessages(prev => [...prev, 'Sent test message to server']);
        } else {
            setMessages(prev => [...prev, 'Failed to send message - not connected']);
        }
    };

    const handleRequestLessonGeneration = () => {
        sendMessage({
            type: 'request_lesson_generation',
            data: {
                topic_id: 'example-topic-123'
            }
        });
    };

    const clearMessages = () => {
        setMessages([]);
    };

    return (
        <div className="p-6 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-4">WebSocket Example</h2>

            {/* Trạng thái kết nối */}
            <div className="mb-6 p-4 border rounded-lg">
                <h3 className="text-lg font-semibold mb-2">Trạng thái kết nối</h3>
                <div className="flex items-center gap-4">
                    <WebSocketStatus showText={true} />
                    <span className="text-sm text-gray-600">
                        Status: {connectionStatus}
                    </span>
                </div>
            </div>

            {/* Controls */}
            <div className="mb-6 p-4 border rounded-lg">
                <h3 className="text-lg font-semibold mb-3">Controls</h3>
                <div className="flex gap-2 flex-wrap">
                    <button
                        onClick={handleSendTestMessage}
                        disabled={!isConnected}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400"
                    >
                        Gửi tin nhắn test
                    </button>

                    <button
                        onClick={handleRequestLessonGeneration}
                        disabled={!isConnected}
                        className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-400"
                    >
                        Yêu cầu tạo bài học
                    </button>

                    <button
                        onClick={clearMessages}
                        className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                    >
                        Xóa tin nhắn
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="p-4 border rounded-lg">
                <h3 className="text-lg font-semibold mb-3">Tin nhắn WebSocket</h3>
                <div className="h-64 overflow-y-auto bg-gray-50 dark:bg-gray-800 p-3 rounded">
                    {messages.length === 0 ? (
                        <p className="text-gray-500 text-center">Chưa có tin nhắn nào...</p>
                    ) : (
                        messages.map((message, index) => (
                            <div key={index} className="mb-2 text-sm font-mono">
                                <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span>{' '}
                                {message}
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Documentation */}
            <div className="mt-6 p-4 border rounded-lg bg-blue-50 dark:bg-blue-900/20">
                <h3 className="text-lg font-semibold mb-2">Cách sử dụng</h3>
                <ul className="text-sm space-y-1">
                    <li>• Component này tự động kết nối WebSocket khi mount</li>
                    <li>• Sử dụng các hooks để lắng nghe tin nhắn theo loại</li>
                    <li>• Kiểm tra trạng thái kết nối trước khi gửi tin nhắn</li>
                    <li>• WebSocket sẽ tự động kết nối lại nếu mất kết nối</li>
                </ul>
            </div>
        </div>
    );
};

export default WebSocketExample; 