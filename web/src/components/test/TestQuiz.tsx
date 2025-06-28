'use client';

import React from 'react';
import { TestSessionWithTest, TestAnswer, TestQuestion } from '@/lib/api';

interface TestQuizProps {
    testSession: TestSessionWithTest;
    currentQuestionIndex: number;
    timeRemaining: number;
    answers: Record<string, TestAnswer>;
    formatTime: (seconds: number) => string;
    getProgress: () => number;
    canSubmit: () => boolean;
    onSubmitAnswer: (questionId: string, answer: TestAnswer) => void;
    onNextQuestion: () => void;
    onPreviousQuestion: () => void;
    onGoToQuestion: (index: number) => void;
    onSubmitTest: () => void;
    isSubmitting: boolean;
}

export const TestQuiz: React.FC<TestQuizProps> = ({
    testSession,
    currentQuestionIndex,
    timeRemaining,
    answers,
    formatTime,
    getProgress,
    canSubmit,
    onSubmitAnswer,
    onNextQuestion,
    onPreviousQuestion,
    onGoToQuestion,
    onSubmitTest,
    isSubmitting
}) => {
    const { test } = testSession;
    const currentQuestion = test.questions[currentQuestionIndex];
    const totalQuestions = test.questions.length;
    const answeredCount = Object.keys(answers).length;

    // Get color based on time remaining
    const getTimeColor = () => {
        const percentage = (timeRemaining / (test.durationMinutes * 60)) * 100;
        if (percentage > 30) return 'text-green-600';
        if (percentage > 10) return 'text-yellow-600';
        return 'text-red-600';
    };

    const handleAnswerChange = (answer: TestAnswer) => {
        onSubmitAnswer(currentQuestion.id, answer);
    };

    const renderQuestion = () => {
        if (!currentQuestion) return null;

        switch (currentQuestion.type) {
            case 'single_choice':
                return (
                    <MultipleChoiceQuestionComponent
                        question={currentQuestion}
                        questionNumber={currentQuestionIndex + 1}
                        selectedAnswer={answers[currentQuestion.id]?.selectedOptionId}
                        onAnswerChange={(selectedOptionId) =>
                            handleAnswerChange({ selectedOptionId })
                        }
                    />
                );
            case 'essay':
                return (
                    <EssayQuestionComponent
                        question={currentQuestion}
                        questionNumber={currentQuestionIndex + 1}
                        answer={answers[currentQuestion.id]?.code || ''}
                        onAnswerChange={(code) =>
                            handleAnswerChange({ code })
                        }
                    />
                );
            default:
                return <div>Loại câu hỏi không được hỗ trợ</div>;
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header with timer and progress */}
            <div className="bg-white shadow-sm border-b sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Progress */}
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center">
                                <svg className="w-5 h-5 text-gray-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                </svg>
                                <span className="text-sm font-medium text-gray-700">
                                    Câu {currentQuestionIndex + 1} / {totalQuestions}
                                </span>
                            </div>
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                                <div
                                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                    style={{ width: `${getProgress()}%` }}
                                ></div>
                            </div>
                            <span className="text-sm text-gray-600">
                                {answeredCount}/{totalQuestions} trả lời
                            </span>
                        </div>

                        {/* Timer */}
                        <div className="flex items-center space-x-4">
                            <div className={`flex items-center ${getTimeColor()}`}>
                                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span className="font-mono text-lg font-semibold">
                                    {formatTime(timeRemaining)}
                                </span>
                            </div>
                            <button
                                onClick={onSubmitTest}
                                disabled={!canSubmit() || isSubmitting}
                                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors disabled:cursor-not-allowed"
                            >
                                {isSubmitting ? 'Đang nộp...' : 'Nộp bài'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Question Navigation Sidebar */}
                    <div className="lg:col-span-1">
                        <div className="bg-white rounded-xl shadow-sm p-6 sticky top-24">
                            <h3 className="font-semibold text-gray-800 mb-4">Danh sách câu hỏi</h3>
                            <div className="grid grid-cols-5 lg:grid-cols-3 gap-2">
                                {test.questions.map((question, index) => {
                                    const isAnswered = answers[question.id];
                                    const isCurrent = index === currentQuestionIndex;

                                    return (
                                        <button
                                            key={question.id}
                                            onClick={() => onGoToQuestion(index)}
                                            className={`
                                                w-10 h-10 rounded-lg text-sm font-medium transition-all
                                                ${isCurrent
                                                    ? 'bg-blue-600 text-white shadow-lg scale-110'
                                                    : isAnswered
                                                        ? 'bg-green-100 text-green-700 hover:bg-green-200'
                                                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                }
                                            `}
                                        >
                                            {index + 1}
                                        </button>
                                    );
                                })}
                            </div>

                            <div className="mt-6 space-y-2 text-sm">
                                <div className="flex items-center">
                                    <div className="w-4 h-4 bg-blue-600 rounded mr-2"></div>
                                    <span className="text-gray-600">Câu hiện tại</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-4 h-4 bg-green-100 border border-green-300 rounded mr-2"></div>
                                    <span className="text-gray-600">Đã trả lời</span>
                                </div>
                                <div className="flex items-center">
                                    <div className="w-4 h-4 bg-gray-100 border border-gray-300 rounded mr-2"></div>
                                    <span className="text-gray-600">Chưa trả lời</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Question Area */}
                    <div className="lg:col-span-3">
                        <div className="bg-white rounded-xl shadow-sm p-8">
                            {renderQuestion()}

                            {/* Navigation Buttons */}
                            <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
                                <button
                                    onClick={onPreviousQuestion}
                                    disabled={currentQuestionIndex === 0}
                                    className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                                >
                                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                                    </svg>
                                    Câu trước
                                </button>

                                <div className="text-center">
                                    <span className="text-sm text-gray-500">
                                        Câu {currentQuestionIndex + 1} / {totalQuestions}
                                    </span>
                                </div>

                                <button
                                    onClick={onNextQuestion}
                                    disabled={currentQuestionIndex === totalQuestions - 1}
                                    className="flex items-center px-4 py-2 text-blue-600 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
                                >
                                    Câu tiếp
                                    <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Multiple Choice Question Component
const MultipleChoiceQuestionComponent: React.FC<{
    question: TestQuestion;
    questionNumber: number;
    selectedAnswer?: string;
    onAnswerChange: (selectedOptionId: string) => void;
}> = ({ question, questionNumber, selectedAnswer, onAnswerChange }) => {
    return (
        <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-6">
                Câu {questionNumber}
            </h2>

            <div className="text-gray-700 mb-6" dangerouslySetInnerHTML={{ __html: question.content }} />

            <div className="space-y-3">
                {question.options?.map((option, index) => {
                    const optionValue = index.toString(); // Use index as option value
                    return (
                        <label
                            key={index}
                            className={`
                                flex items-center p-4 rounded-lg border-2 cursor-pointer transition-all
                                ${selectedAnswer === optionValue
                                    ? 'border-blue-500 bg-blue-50'
                                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                                }
                            `}
                        >
                            <input
                                type="radio"
                                name={`question-${question.id}`}
                                value={optionValue}
                                checked={selectedAnswer === optionValue}
                                onChange={() => onAnswerChange(optionValue)}
                                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 focus:ring-blue-500"
                            />
                            <span className="ml-3 text-gray-800">
                                {String.fromCharCode(65 + index)}. {option}
                            </span>
                        </label>
                    );
                })}
            </div>
        </div>
    );
};

// Essay Question Component
const EssayQuestionComponent: React.FC<{
    question: TestQuestion;
    questionNumber: number;
    answer: string;
    onAnswerChange: (answer: string) => void;
}> = ({ question, questionNumber, answer, onAnswerChange }) => {
    return (
        <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-6">
                Câu {questionNumber}
            </h2>

            <div className="text-gray-700 mb-6" dangerouslySetInnerHTML={{ __html: question.content }} />

            <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nhập câu trả lời của bạn:
                </label>
                <textarea
                    value={answer}
                    onChange={(e) => onAnswerChange(e.target.value)}
                    className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm resize-none"
                    placeholder="Nhập câu trả lời hoặc code của bạn..."
                />
            </div>
        </div>
    );
}; 