'use client';

import React from 'react';
import { useWebSocket } from '@/contexts/WebSocketContext';

interface WebSocketStatusProps {
    showText?: boolean;
    className?: string;
}

export const WebSocketStatus: React.FC<WebSocketStatusProps> = ({
    showText = false,
    className = ''
}) => {
    const { connectionStatus, isConnected } = useWebSocket();

    const getStatusColor = () => {
        switch (connectionStatus) {
            case 'connected':
                return 'bg-green-500';
            case 'connecting':
                return 'bg-yellow-500';
            case 'disconnected':
                return 'bg-red-500';
            case 'error':
                return 'bg-red-600';
            default:
                return 'bg-gray-500';
        }
    };

    const getStatusText = () => {
        switch (connectionStatus) {
            case 'connected':
                return 'Đã kết nối';
            case 'connecting':
                return 'Đang kết nối...';
            case 'disconnected':
                return 'Mất kết nối';
            case 'error':
                return 'Lỗi kết nối';
            default:
                return 'Không xác định';
        }
    };

    return (
        <div className={`flex items-center gap-2 ${className}`}>
            <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${connectionStatus === 'connecting' ? 'animate-pulse' : ''
                }`} />
            {showText && (
                <span className={`text-sm ${isConnected ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                    }`}>
                    {getStatusText()}
                </span>
            )}
        </div>
    );
};

export default WebSocketStatus; 