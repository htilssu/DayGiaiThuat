'use client';

import { RootState, useAppSelector } from '@/lib/store';
import { getCookie } from '@/lib/utils/cookie';
import React, { createContext, useContext, useEffect, useState, useRef, ReactNode } from 'react';

interface WebSocketMessage {
    type: string;
    data: any;
    timestamp?: string;
}

interface WebSocketContextType {
    socket: WebSocket | null;
    isConnected: boolean;
    sendMessage: (message: WebSocketMessage) => void;
    lastMessage: WebSocketMessage | null;
    connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

interface WebSocketProviderProps {
    children: ReactNode;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
    const [socket, setSocket] = useState<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const loggingInterval = useRef<NodeJS.Timeout | null>(null);
    const { user } = useAppSelector((state: RootState) => state.user);
    const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
    const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'error'>('disconnected');
    const reconnectAttempts = useRef(0);
    const maxReconnectAttempts = 5;
    const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

    const getWebSocketUrl = () => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = process.env.NEXT_PUBLIC_API_URL?.replace(/^https?:\/\//, '') || 'localhost:8000';
        return `${protocol}//${host}/ws?token=${user?.id}`;
    };

    const connectWebSocket = () => {
        try {
            setConnectionStatus('connecting');
            const wsUrl = getWebSocketUrl();
            const ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket kết nối thành công');
                setIsConnected(true);
                setConnectionStatus('connected');
                reconnectAttempts.current = 0;
            };

            ws.onmessage = (event) => {
                try {
                    const message: WebSocketMessage = JSON.parse(event.data);
                    setLastMessage(message);
                    console.log('Nhận tin nhắn WebSocket:', message);
                } catch (error) {
                    console.error('Lỗi parse tin nhắn WebSocket:', error);
                }
            };

            ws.onclose = (event) => {
                console.log('WebSocket đóng kết nối:', event.code, event.reason);
                setIsConnected(false);
                setSocket(null);
                setConnectionStatus('disconnected');

                const delay = Math.pow(2, reconnectAttempts.current) * 1000; // Exponential backoff
                reconnectTimeout.current = setTimeout(() => {
                    reconnectAttempts.current++;
                    console.log(`Thử kết nối lại WebSocket lần ${reconnectAttempts.current}/${maxReconnectAttempts}`);
                    connectWebSocket();
                }, delay);
            };

            ws.onerror = (error) => {
                console.error('Lỗi WebSocket:', error);
                setConnectionStatus('error');
            };

            setSocket(ws);
        } catch (error) {
            console.error('Lỗi tạo kết nối WebSocket:', error);
            setConnectionStatus('error');
        }
    };

    const sendMessage = (message: WebSocketMessage) => {
        if (socket?.readyState === WebSocket.OPEN) {
            const messageWithTimestamp = {
                ...message,
                timestamp: new Date().toISOString()
            };
            socket.send(JSON.stringify(messageWithTimestamp));
        } else {
            console.warn('WebSocket chưa sẵn sàng để gửi tin nhắn');
        }
    };

    // Kết nối WebSocket khi component mount
    useEffect(() => {
        if (!user) return;
        if (socket?.readyState === WebSocket.OPEN) {
            socket.close(1000, 'Reconnect');
        }
        connectWebSocket();

        return () => {
            if (reconnectTimeout.current) {
                clearTimeout(reconnectTimeout.current);
            }
            if (socket) {
                socket.close(1000, 'Component unmounted');
            }
        };
    }, [user]);

    const value: WebSocketContextType = {
        socket,
        isConnected,
        sendMessage,
        lastMessage,
        connectionStatus
    };

    return (
        <WebSocketContext.Provider value={value}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = (): WebSocketContextType => {
    const context = useContext(WebSocketContext);
    if (context === undefined) {
        throw new Error('useWebSocket phải được sử dụng trong WebSocketProvider');
    }
    return context;
};

export default WebSocketContext;
export const socketType = {
    LEARN_COMPLETE_LESSON: 'learn.complete_lesson',
    LEARN_START_LESSON: 'learn.start_lesson',
    CHAT: 'chat',
    NOTIFICATION: 'notification',
    TEST_SESSION_COMPLETE: 'test_session.complete',
    GENERAL: 'general',
}