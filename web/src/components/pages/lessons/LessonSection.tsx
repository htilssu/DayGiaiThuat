'use client';

import React, { useState } from 'react';
import { CheckCircleIcon } from '@heroicons/react/24/solid';
import CodeSection from './CodeSection';

interface LessonSectionData {
    type: 'text' | 'code' | 'quiz' | string;
    content: string;
    options?: Record<string, string>;
    answer?: string;
    explanation?: string;
    language?: string;
}

interface LessonSectionProps {
    section: LessonSectionData;
    index: number;
    className?: string;
    style?: React.CSSProperties;
}

/**
 * Component hiển thị một section trong bài học
 */
export const LessonSection: React.FC<LessonSectionProps> = ({
    section,
    index,
    className = '',
    style
}) => {
    const [selectedAnswer, setSelectedAnswer] = useState<string>('');
    const [showAnswer, setShowAnswer] = useState<boolean>(false);
    const [isAnswered, setIsAnswered] = useState<boolean>(false);

    const handleAnswerSelect = (answer: string) => {
        setSelectedAnswer(answer);
    };

    const handleSubmitAnswer = () => {
        if (selectedAnswer) {
            setShowAnswer(true);
            setIsAnswered(true);
        }
    };

    const isCorrectAnswer = selectedAnswer === section.answer;

    const renderTextSection = () => (
        <div className="prose max-w-none dark:prose-invert">
            <div
                dangerouslySetInnerHTML={{ __html: section.content }}
                className="text-foreground"
            />
        </div>
    );

    const renderCodeSection = () => (
        <CodeSection
            content={section.content}
            language={section.language || 'javascript'}
            title="Ví dụ mã nguồn"
            showLineNumbers={true}
        />
    );

    const renderQuizSection = () => (
        <div>
            <h3 className="text-lg font-semibold mb-3 text-foreground flex items-center gap-2">
                <span className="text-2xl">🤔</span>
                Câu hỏi kiểm tra
            </h3>

            <div className="prose max-w-none mb-4 dark:prose-invert">
                <div
                    dangerouslySetInnerHTML={{ __html: section.content }}
                    className="text-foreground"
                />
            </div>

            {section.options && (
                <div className="space-y-3">
                    {Object.entries(section.options).map(([key, value]: [string, string]) => (
                        <label
                            key={key}
                            className={`flex items-center space-x-3 p-3 rounded-lg border-2 cursor-pointer transition-all hover:bg-foreground/5 ${selectedAnswer === key
                                ? 'border-primary bg-primary/10'
                                : 'border-foreground/20'
                                } ${showAnswer && section.answer === key
                                    ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                                    : ''
                                } ${showAnswer && selectedAnswer === key && section.answer !== key
                                    ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                                    : ''
                                }`}
                        >
                            <input
                                type="radio"
                                name={`quiz-${index}`}
                                value={key}
                                checked={selectedAnswer === key}
                                onChange={() => handleAnswerSelect(key)}
                                disabled={isAnswered}
                                className="text-primary focus:ring-primary"
                            />
                            <span className="flex-1 text-foreground">{value}</span>
                            {showAnswer && section.answer === key && (
                                <CheckCircleIcon className="h-5 w-5 text-green-500" />
                            )}
                        </label>
                    ))}
                </div>
            )}

            {!isAnswered && selectedAnswer && (
                <div className="mt-4">
                    <button
                        onClick={handleSubmitAnswer}
                        className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
                    >
                        Kiểm tra đáp án
                    </button>
                </div>
            )}

            {showAnswer && (
                <div className={`mt-4 p-4 rounded-lg ${isCorrectAnswer
                    ? 'bg-green-50 dark:bg-green-900/20 border-l-4 border-green-500'
                    : 'bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500'
                    }`}>
                    <div className="flex items-center gap-2 mb-2">
                        {isCorrectAnswer ? (
                            <>
                                <CheckCircleIcon className="h-5 w-5 text-green-600" />
                                <span className="font-semibold text-green-800 dark:text-green-400">
                                    Chính xác! 🎉
                                </span>
                            </>
                        ) : (
                            <>
                                <span className="text-2xl">❌</span>
                                <span className="font-semibold text-red-800 dark:text-red-400">
                                    Chưa đúng, hãy thử lại!
                                </span>
                            </>
                        )}
                    </div>

                    <div className="text-sm text-foreground/80">
                        <strong>Đáp án đúng:</strong> {section.options?.[section.answer || '']}
                    </div>

                    {section.explanation && (
                        <div className="mt-2 text-sm text-foreground/70">
                            <strong>Giải thích:</strong> {section.explanation}
                        </div>
                    )}
                </div>
            )}
        </div>
    );

    const renderDefaultSection = () => (
        <div className="prose max-w-none dark:prose-invert">
            <div
                dangerouslySetInnerHTML={{ __html: section.content }}
                className="text-foreground"
            />
        </div>
    );

    const renderSectionContent = () => {
        switch (section.type) {
            case 'text':
                return renderTextSection();
            case 'code':
                return renderCodeSection();
            case 'quiz':
                return renderQuizSection();
            default:
                return renderDefaultSection();
        }
    };

    return (
        <div
            className={`bg-card rounded-xl p-6 shadow-sm border border-border theme-transition ${className}`}
            style={style}
        >
            {renderSectionContent()}
        </div>
    );
};

export default LessonSection; 