'use client';

import React, { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAppSelector } from '@/lib/store';
import { useTestSession } from '@/hooks/useTestSession';
import { TestQuiz } from '@/components/test/TestQuiz';

const ClientPage: React.FC = () => {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.id as string;
    const userState = useAppSelector((state) => state.user);
    const {
        state,
        testSession,
        error,
        currentQuestionIndex,
        timeRemaining,
        answers,
        isSubmitting,
        startTest,
        submitAnswer,
        submitTest,
        nextQuestion,
        previousQuestion,
        goToQuestion,
        formatTime,
        getProgress,
        canSubmit,
    } = useTestSession(sessionId);


    // Redirect if not authenticated
    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
            router.push('/auth/login');
        }
    }, [userState, router]);

    // Show loading during auth check
    if (userState.isLoading || userState.isInitial) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Đang kiểm tra quyền truy cập...</p>
                </div>
            </div>
        );
    }

    // If not authenticated, will be redirected by useEffect
    if (!userState.user) {
        return null;
    }

    // Loading state
    if (state === 'loading') {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Đang tải bài kiểm tra...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (state === 'error') {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center max-w-md mx-auto p-6">
                    <div className="bg-red-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                        </svg>
                    </div>
                    <h2 className="text-xl font-semibold text-gray-800 mb-2">Có lỗi xảy ra</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                        Thử lại
                    </button>
                </div>
            </div>
        );
    }


    // Quiz state - show test questions
    if (state === 'quiz' && testSession) {
        return (
            <TestQuiz
                testSession={testSession}
                currentQuestionIndex={currentQuestionIndex}
                timeRemaining={timeRemaining}
                answers={answers}
                formatTime={formatTime}
                getProgress={getProgress}
                canSubmit={canSubmit}
                onSubmitAnswer={submitAnswer}
                onNextQuestion={nextQuestion}
                onPreviousQuestion={previousQuestion}
                onGoToQuestion={goToQuestion}
                onSubmitTest={submitTest}
                isSubmitting={isSubmitting}
            />
        );
    }

    // Submitted state - redirect to results page
    if (state === 'submitted' && testSession) {
        // Redirect to results page after successful submission
        useEffect(() => {
            const timer = setTimeout(() => {
                router.push(`/tests/results/${sessionId}`);
            }, 2000); // Show loading for 2 seconds then redirect

            return () => clearTimeout(timer);
        }, []);

        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl mx-auto text-center">
                    <div className="mx-auto w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-6">
                        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                    </div>

                    <h1 className="text-2xl font-bold text-gray-800 mb-4">
                        Bài kiểm tra đã được nộp thành công!
                    </h1>

                    <p className="text-gray-600 mb-6">
                        Đang chuyển hướng đến trang kết quả...
                    </p>

                    <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    </div>
                </div>
            </div>
        );
    }

    // Fallback
    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="text-center">
                <p className="text-gray-600">Đang khởi tạo bài kiểm tra...</p>
            </div>
        </div>
    );

};

export default ClientPage; 