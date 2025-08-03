import React from 'react';

/**
 * Component loading spinner đơn giản
 */
export default function LoadingSpinner() {
    return (
        <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
            <div className="flex flex-col items-center space-y-4">
                {/* Spinner */}
                <div className="relative">
                    <div className="w-12 h-12 border-4 border-gray-200 rounded-full animate-spin border-t-blue-600"></div>
                </div>

                {/* Loading text */}
                <div className="text-gray-600 font-medium">
                    Đang tải...
                </div>

                {/* Optional: Brand name */}
                <div className="text-sm text-gray-400">
                    AI Giải Thuật
                </div>
            </div>
        </div>
    );
}
