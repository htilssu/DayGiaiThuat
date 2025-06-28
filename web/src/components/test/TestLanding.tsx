'use client';

import React from 'react';
import { TestSessionWithTest } from '@/lib/api';

interface TestLandingProps {
    testSession: TestSessionWithTest;
    timeRemaining: number;
    formatTime: (seconds: number) => string;
    onStartTest: () => void;
    isStarting?: boolean;
}

export const TestLanding: React.FC<TestLandingProps> = ({
    testSession,
    timeRemaining,
    formatTime,
    onStartTest,
    isStarting = false
}) => {
    const { test } = testSession;

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
            <div className="max-w-2xl w-full">
                {/* Header Card */}
                <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
                    <div className="text-center">
                        <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>

                        <h1 className="text-3xl font-bold text-gray-800 mb-2">
                            Sẵn sàng làm bài kiểm tra?
                        </h1>

                        <p className="text-gray-600 text-lg">
                            Hãy đọc kỹ hướng dẫn và chuẩn bị tinh thần trước khi bắt đầu
                        </p>
                    </div>
                </div>

                {/* Test Info Card */}
                <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
                    <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
                        <svg className="w-6 h-6 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Thông tin bài kiểm tra
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Duration */}
                        <div className="flex items-center p-4 bg-orange-50 rounded-xl">
                            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mr-4">
                                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-800">Thời gian làm bài</h3>
                                <p className="text-orange-600 font-medium">{formatTime(timeRemaining)}</p>
                            </div>
                        </div>

                        {/* Questions */}
                        <div className="flex items-center p-4 bg-green-50 rounded-xl">
                            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-800">Số câu hỏi</h3>
                                <p className="text-green-600 font-medium">{test.questions.length} câu</p>
                            </div>
                        </div>

                        {/* Passing Score */}
                        {test.passingScore && (
                            <div className="flex items-center p-4 bg-purple-50 rounded-xl">
                                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-800">Điểm đạt</h3>
                                    <p className="text-purple-600 font-medium">{test.passingScore}%</p>
                                </div>
                            </div>
                        )}

                        {/* Session ID */}
                        <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mr-4">
                                <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                                </svg>
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-800">Mã phiên</h3>
                                <p className="text-gray-600 font-mono text-sm">{testSession.id}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Instructions Card */}
                <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
                    <h2 className="text-xl font-semibold text-gray-800 mb-6 flex items-center">
                        <svg className="w-6 h-6 text-yellow-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                        Lưu ý quan trọng
                    </h2>

                    <div className="space-y-4">
                        <div className="flex items-start">
                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-3 mr-3 flex-shrink-0"></div>
                            <p className="text-gray-700">
                                <strong>Thời gian:</strong> Bài kiểm tra sẽ tự động nộp khi hết thời gian. Hãy quản lý thời gian hợp lý.
                            </p>
                        </div>

                        <div className="flex items-start">
                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-3 mr-3 flex-shrink-0"></div>
                            <p className="text-gray-700">
                                <strong>Lưu đáp án:</strong> Các câu trả lời sẽ được tự động lưu khi bạn chọn hoặc nhập.
                            </p>
                        </div>

                        <div className="flex items-start">
                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-3 mr-3 flex-shrink-0"></div>
                            <p className="text-gray-700">
                                <strong>Điều hướng:</strong> Bạn có thể di chuyển qua lại giữa các câu hỏi trong suốt quá trình làm bài.
                            </p>
                        </div>

                        <div className="flex items-start">
                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-3 mr-3 flex-shrink-0"></div>
                            <p className="text-gray-700">
                                <strong>Kết nối:</strong> Đảm bảo kết nối internet ổn định để tránh mất dữ liệu.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Start Button */}
                <div className="text-center">
                    <button
                        onClick={onStartTest}
                        disabled={isStarting}
                        className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-semibold py-4 px-12 rounded-2xl text-lg shadow-lg transform transition-all duration-200 hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed focus:outline-none focus:ring-4 focus:ring-blue-200"
                    >
                        {isStarting ? (
                            <div className="flex items-center">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Đang chuẩn bị...
                            </div>
                        ) : (
                            <div className="flex items-center">
                                <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.01M15 10h1.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Bắt đầu làm bài
                            </div>
                        )}
                    </button>

                    <p className="text-gray-600 mt-4 text-sm">
                        Nhấn nút để bắt đầu bài kiểm tra
                    </p>
                </div>
            </div>
        </div>
    );
}; 