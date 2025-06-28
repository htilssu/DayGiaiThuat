'use client';

import React from 'react';
import { TestLanding } from './TestLanding';
import { TestQuiz } from './TestQuiz';
import { useTestSession } from '@/hooks';

interface TestPageNewProps {
    sessionId: string;
}

export const TestPageNew: React.FC<TestPageNewProps> = ({ sessionId }) => {
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

    // Landing state - show test information before starting
    if (state === 'landing' && testSession) {
        return (
            <TestLanding
                testSession={testSession}
                timeRemaining={timeRemaining}
                formatTime={formatTime}
                onStartTest={startTest}
                isStarting={isSubmitting}
            />
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

    // Submitted state - show completion message
    if (state === 'submitted' && testSession) {
        const { test } = testSession;
        const score = testSession.score ?? 0;
        const correctAnswers = testSession.correctAnswers ?? 0;
        const totalQuestions = test.questions.length;
        const passed = test.passingScore ? score >= test.passingScore : true;

        return (
            <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
                <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl mx-auto text-center">
                    <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-6 ${passed ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                        {passed ? (
                            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        ) : (
                            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        )}
                    </div>

                    <h1 className="text-2xl font-bold text-gray-800 mb-4">
                        {passed ? 'Chúc mừng! Bạn đã hoàn thành bài kiểm tra!' : 'Bài kiểm tra đã hoàn thành'}
                    </h1>

                    <div className="bg-gray-50 rounded-xl p-6 mb-6">
                        <div className="grid grid-cols-3 gap-4 text-center">
                            <div>
                                <div className="text-2xl font-bold text-blue-600">{score}%</div>
                                <div className="text-sm text-gray-600">Điểm số</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-green-600">{correctAnswers}</div>
                                <div className="text-sm text-gray-600">Câu đúng</div>
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-gray-600">{totalQuestions}</div>
                                <div className="text-sm text-gray-600">Tổng câu</div>
                            </div>
                        </div>
                    </div>

                    {test.passingScore && (
                        <p className={`text-sm mb-6 ${passed ? 'text-green-600' : 'text-red-600'}`}>
                            {passed
                                ? `Bạn đã đạt điểm tối thiểu ${test.passingScore}% để vượt qua bài kiểm tra!`
                                : `Bạn cần đạt tối thiểu ${test.passingScore}% để vượt qua bài kiểm tra.`
                            }
                        </p>
                    )}

                    <div className="flex gap-4 justify-center">
                        <button
                            onClick={() => window.history.back()}
                            className="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                        >
                            Quay lại
                        </button>
                        {test.topicId && (
                            <button
                                onClick={() => window.location.href = `/topics/${test.topicId}`}
                                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                            >
                                Về chủ đề
                            </button>
                        )}
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