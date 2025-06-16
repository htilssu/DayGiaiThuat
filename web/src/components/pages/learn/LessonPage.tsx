"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";

interface LessonSection {
    type: "text" | "code" | "image" | "quiz";
    content: string;
    options?: string[];
    answer?: number;
    explanation?: string;
}

interface Lesson {
    id: string;
    title: string;
    description: string;
    topicId: string;
    topicTitle: string;
    sections: LessonSection[];
    nextLessonId?: string;
    prevLessonId?: string;
}

interface LessonPageProps {
    lesson: Lesson;
}

export function LessonPage({ lesson }: LessonPageProps) {
    const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
    const [showExplanation, setShowExplanation] = useState(false);
    const [isCompleted, setIsCompleted] = useState(false);

    const currentSection = lesson.sections[currentSectionIndex];
    const isLastSection = currentSectionIndex === lesson.sections.length - 1;
    const isQuiz = currentSection?.type === "quiz";

    const handleNext = () => {
        if (isQuiz && selectedAnswer === null) return;

        if (isLastSection) {
            setIsCompleted(true);
        } else {
            setCurrentSectionIndex(currentSectionIndex + 1);
            setSelectedAnswer(null);
            setShowExplanation(false);
        }
    };

    const handlePrev = () => {
        if (currentSectionIndex > 0) {
            setCurrentSectionIndex(currentSectionIndex - 1);
            setSelectedAnswer(null);
            setShowExplanation(false);
        }
    };

    const handleAnswerSelect = (index: number) => {
        setSelectedAnswer(index);
        if (isQuiz) {
            setShowExplanation(true);
        }
    };

    const renderSection = (section: LessonSection) => {
        switch (section.type) {
            case "text":
                return (
                    <div className="prose max-w-none">
                        <div dangerouslySetInnerHTML={{ __html: section.content }} />
                    </div>
                );
            case "code":
                return (
                    <pre className="bg-foreground/5 p-4 rounded-lg overflow-x-auto">
                        <code>{section.content}</code>
                    </pre>
                );
            case "image":
                return (
                    <div className="flex justify-center">
                        <img src={section.content} alt="Lesson illustration" className="max-w-full rounded-lg" />
                    </div>
                );
            case "quiz":
                return (
                    <div>
                        <h3 className="text-xl font-semibold mb-4">Câu hỏi:</h3>
                        <p className="mb-6">{section.content}</p>
                        <div className="space-y-3">
                            {section.options?.map((option, index) => (
                                <div
                                    key={index}
                                    onClick={() => handleAnswerSelect(index)}
                                    className={`p-4 border rounded-lg cursor-pointer transition-all ${selectedAnswer === index
                                        ? selectedAnswer === section.answer
                                            ? "border-green-500 bg-green-50"
                                            : "border-red-500 bg-red-50"
                                        : "border-gray-200 hover:border-primary/50"
                                        }`}
                                >
                                    <div className="flex items-center">
                                        <div
                                            className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${selectedAnswer === index
                                                ? selectedAnswer === section.answer
                                                    ? "bg-green-500 text-white"
                                                    : "bg-red-500 text-white"
                                                : "bg-foreground/10"
                                                }`}
                                        >
                                            {String.fromCharCode(65 + index)}
                                        </div>
                                        <span>{option}</span>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {showExplanation && (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`mt-6 p-4 rounded-lg ${selectedAnswer === section.answer
                                    ? "bg-green-100 border border-green-300"
                                    : "bg-red-100 border border-red-300"
                                    }`}
                            >
                                <div className="flex items-center mb-2">
                                    {selectedAnswer === section.answer ? (
                                        <>
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                                            </svg>
                                            <span className="font-semibold">Chính xác!</span>
                                        </>
                                    ) : (
                                        <>
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                            </svg>
                                            <span className="font-semibold">Chưa chính xác!</span>
                                        </>
                                    )}
                                </div>
                                <p>{section.explanation}</p>
                                {selectedAnswer !== section.answer && (
                                    <p className="mt-2 font-semibold">
                                        Đáp án đúng là: {String.fromCharCode(65 + (section.answer || 0))}
                                    </p>
                                )}
                            </motion.div>
                        )}
                    </div>
                );
            default:
                return <p>Không hỗ trợ loại nội dung này</p>;
        }
    };

    return (
        <div className="min-h-screen pb-20">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center mb-2">
                        <Link href={`/topics/${lesson.topicId}`} className="text-primary hover:underline">
                            {lesson.topicTitle}
                        </Link>
                        <span className="mx-2">•</span>
                        <span>Bài {lesson.id}</span>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold">{lesson.title}</h1>
                    <p className="text-foreground/70 mt-2">{lesson.description}</p>
                </div>

                {/* Progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-8">
                    <div
                        className="h-2 rounded-full bg-primary"
                        style={{ width: `${((currentSectionIndex + 1) / lesson.sections.length) * 100}%` }}
                    ></div>
                </div>

                {/* Lesson content */}
                {isCompleted ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-green-50 border border-green-200 rounded-xl p-8 text-center"
                    >
                        <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                        </div>
                        <h2 className="text-2xl font-bold mb-4">Chúc mừng! Bạn đã hoàn thành bài học</h2>
                        <p className="text-foreground/70 mb-6">
                            Bạn đã học xong bài {lesson.title}. Hãy tiếp tục với bài học tiếp theo để nâng cao kiến thức của mình.
                        </p>
                        <div className="flex flex-wrap justify-center gap-4">
                            {lesson.nextLessonId ? (
                                <Link
                                    href={`/topics/${lesson.topicId}/lessons/${lesson.nextLessonId}`}
                                    className="px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all"
                                >
                                    Bài học tiếp theo
                                </Link>
                            ) : (
                                <Link
                                    href={`/topics/${lesson.topicId}`}
                                    className="px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all"
                                >
                                    Quay lại chủ đề
                                </Link>
                            )}
                            <Link
                                href="/learn"
                                className="px-6 py-3 bg-background border border-primary text-primary font-semibold rounded-lg hover:bg-primary/5 transition-all"
                            >
                                Lộ trình học tập
                            </Link>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key={currentSectionIndex}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="bg-white rounded-xl p-6 md:p-8 shadow-sm border border-foreground/10"
                    >
                        {renderSection(currentSection)}

                        <div className="flex justify-between mt-8">
                            <button
                                onClick={handlePrev}
                                disabled={currentSectionIndex === 0}
                                className={`px-4 py-2 rounded-lg ${currentSectionIndex === 0
                                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                                    : "bg-foreground/10 hover:bg-foreground/20"
                                    }`}
                            >
                                Quay lại
                            </button>
                            <button
                                onClick={handleNext}
                                disabled={isQuiz && selectedAnswer === null}
                                className={`px-6 py-2 rounded-lg ${isQuiz && selectedAnswer === null
                                    ? "bg-gray-100 text-gray-400 cursor-not-allowed"
                                    : "bg-primary text-white hover:bg-primary/90"
                                    }`}
                            >
                                {isLastSection ? "Hoàn thành" : "Tiếp theo"}
                            </button>
                        </div>
                    </motion.div>
                )}

                {/* Section indicators */}
                <div className="flex justify-center mt-8">
                    {lesson.sections.map((_, index) => (
                        <div
                            key={index}
                            className={`w-3 h-3 rounded-full mx-1 ${index === currentSectionIndex
                                ? "bg-primary"
                                : index < currentSectionIndex
                                    ? "bg-primary/50"
                                    : "bg-gray-300"
                                }`}
                        ></div>
                    ))}
                </div>
            </div>
        </div>
    );
}
