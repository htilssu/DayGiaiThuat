"use client";


import { CodeBlock } from "@/components/ui/CodeBlock";
import { MarkdownRenderer } from "@/components/ui/MarkdownRenderer";
import { socketType, useWebSocket } from "@/contexts/WebSocketContext";
import { lessonsApi } from "@/lib/api";
import { Lesson, LessonSection } from "@/lib/api/lessons";
import { processLessonContent } from "@/lib/contentUtils";
import { useAppDispatch, useAppSelector } from "@/lib/store";
import { setState } from "@/lib/store/tutor";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface LessonPageProps {
    topicId: string;
    lessonId: string;
}

export function LessonPage({ topicId, lessonId }: LessonPageProps) {
    const tutor = useAppSelector(state => state.tutor);
    const dispatch = useAppDispatch();
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [showExplanation, setShowExplanation] = useState(false);
    const [isCompleted, setIsCompleted] = useState(false);
    const [nextLessonId, setNextLessonId] = useState<number | null>(null);
    const { data: lesson } = useQuery({
        queryKey: ["lesson", lessonId],
        queryFn: async (): Promise<Lesson> => {
            const data = await lessonsApi.getLessonById(Number(lessonId));
            if (!data) {
                throw new Error("Lesson not found");
            }
            setIsLoading(false);
            dispatch(setState({
                sessionId: null,
                type: "lesson",
                contextId: data.id.toString()
            }));
            setCurrentSectionIndex(0);
            setSelectedAnswer(null);
            setShowExplanation(false);
            setIsCompleted(data.isCompleted || false);
            setNextLessonId(data.nextLessonId || null);
            if (data.isCompleted) {
                setCurrentSectionIndex((data?.sections?.length ?? 1) - 1);
            }
            return data;
        },
    });
    const router = useRouter();

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <div className="h-8 w-1/2 mx-auto bg-foreground/10 rounded mb-4 animate-pulse"></div>
                    <div className="h-6 w-1/3 mx-auto bg-foreground/10 rounded mb-2 animate-pulse"></div>
                    <div className="h-4 w-1/4 mx-auto bg-foreground/10 rounded mb-6 animate-pulse"></div>
                    <div className="h-40 w-full bg-foreground/10 rounded mb-6 animate-pulse"></div>
                </div>
            </div>
        );
    }


    if (error || !lesson) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold mb-4 text-accent">{error || "Bài học không tồn tại"}</h2>
                    <p className="text-foreground/70 mb-6">Không tìm thấy bài học hoặc bài học đã bị xóa.</p>
                    <Link href={topicId ? `/topics/${topicId}` : "/learn"} className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
                        Quay lại chủ đề
                    </Link>
                </div>
            </div>
        );
    }

    if (!lesson.sections || !Array.isArray(lesson.sections) || lesson.sections.length === 0) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <h2 className="text-2xl font-bold mb-4 text-accent">Bài học không có nội dung</h2>
                    <p className="text-foreground/70 mb-6">Hiện tại bài học này chưa có nội dung hoặc đã bị xóa.</p>
                    <Link href={topicId ? `/topics/${topicId}` : "/learn"} className="px-6 py-3 bg-primary text-white rounded-lg hover:opacity-90 transition">
                        Quay lại chủ đề
                    </Link>
                </div>
            </div>
        );
    }

    const currentSection = lesson.sections[currentSectionIndex];
    const isLastSection = currentSectionIndex === lesson.sections.length - 1;
    const isQuiz = currentSection?.type === "quiz";

    const handleNext = async () => {
        if (isQuiz && selectedAnswer === null) return;

        if (isQuiz && selectedAnswer !== currentSection.answer) return;

        if (isLastSection) {
            setIsCompleted(true);
            const data = await lessonsApi.completeLesson(lesson.id);
            if (data.isCompleted) {
                setNextLessonId(data.nextLessonId);
            }
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

    const handleAnswerSelect = (answerKey: string) => {
        setSelectedAnswer(answerKey);
        if (isQuiz) {
            setShowExplanation(true);
        }
    };

    const renderSection = (section: LessonSection) => {
        const { content, isMarkdown, isHtml, language } = processLessonContent(section.content, section.type);

        switch (section.type) {
            case "text":
                if (isMarkdown) {
                    return (
                        <MarkdownRenderer
                            content={content}
                            className="prose-lg"
                        />
                    );
                } else if (isHtml) {
                    return (
                        <div className="prose prose-slate max-w-none prose-lg">
                            <div dangerouslySetInnerHTML={{ __html: content }} />
                        </div>
                    );
                } else {
                    return (
                        <div className="prose prose-slate max-w-none prose-lg">
                            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{content}</p>
                        </div>
                    );
                }
            case "teaching":
                return (
                    <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                        <div className="flex items-center mb-4">
                            <svg className="w-6 h-6 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                            <h3 className="text-lg font-semibold text-blue-800">Bài giảng</h3>
                        </div>
                        {isMarkdown ? (
                            <MarkdownRenderer
                                content={content}
                                className="prose-blue"
                            />
                        ) : isHtml ? (
                            <div className="prose prose-blue max-w-none">
                                <div dangerouslySetInnerHTML={{ __html: content }} />
                            </div>
                        ) : (
                            <div className="prose prose-blue max-w-none">
                                <p className="text-blue-900 leading-relaxed whitespace-pre-wrap">{content}</p>
                            </div>
                        )}
                    </div>
                );
            case "code":
                return (
                    <div className="space-y-4">
                        <div className="flex items-center mb-4">
                            <svg className="w-5 h-5 text-gray-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                            </svg>
                            <h4 className="text-lg font-semibold text-gray-700">Ví dụ Code</h4>
                        </div>
                        <CodeBlock
                            code={content}
                            language={language}
                            showLineNumbers={true}
                            className="max-w-full"
                        />
                    </div>
                );
            case "image":
                return (
                    <div className="flex justify-center">
                        <img src={section.content} alt="Lesson illustration" className="max-w-full rounded-lg shadow-md" />
                    </div>
                );
            case "quiz":
                return (
                    <div className="bg-amber-50 p-6 rounded-lg border border-amber-200">
                        <div className="flex items-center mb-4">
                            <svg className="w-6 h-6 text-amber-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <h3 className="text-lg font-semibold text-amber-800">Câu hỏi kiểm tra</h3>
                        </div>
                        <div className="mb-6">
                            {isMarkdown ? (
                                <MarkdownRenderer
                                    content={content}
                                    className="prose-amber mb-4"
                                />
                            ) : (
                                <p className="text-amber-900 leading-relaxed whitespace-pre-wrap">{content}</p>
                            )}
                        </div>
                        <div className="space-y-3">
                            {section.options && typeof section.options === 'object'
                                ? Object.entries(section.options).map(([key, value]: [string, any]) => {
                                    const isSelected = selectedAnswer === key;
                                    const isCorrect = key === section.answer;
                                    const isIncorrect = isSelected && !isCorrect;

                                    return (
                                        <div
                                            key={key}
                                            onClick={() => handleAnswerSelect(key)}
                                            className={`p-4 border rounded-lg cursor-pointer transition-all ${isSelected
                                                ? isCorrect
                                                    ? "border-green-500 bg-green-50"
                                                    : "border-red-500 bg-red-50"
                                                : "border-gray-200 hover:border-primary/50 hover:bg-gray-50"
                                                }`}
                                        >
                                            <div className="flex items-center">
                                                <div
                                                    className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 text-sm font-semibold ${isSelected
                                                        ? isCorrect
                                                            ? "bg-green-500 text-white"
                                                            : "bg-red-500 text-white"
                                                        : "bg-gray-200 text-gray-700"
                                                        }`}
                                                >
                                                    {key}
                                                </div>
                                                <div className="flex-1">
                                                    <MarkdownRenderer
                                                        content={String(value)}
                                                        className="prose-sm mb-0"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })
                                : <p className="text-red-500">Không có lựa chọn nào được cung cấp cho câu hỏi này.</p>
                            }
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
                                            <span className="font-semibold text-green-800">Chính xác!</span>
                                        </>
                                    ) : (
                                        <>
                                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
                                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                            </svg>
                                            <span className="font-semibold text-red-800">Chưa chính xác!</span>
                                        </>
                                    )}
                                </div>
                                <MarkdownRenderer
                                    content={section.explanation || "Không có giải thích."}
                                    className="prose-sm"
                                />
                                {selectedAnswer !== section.answer && (
                                    <p className="mt-2 font-semibold text-gray-700">
                                        Đáp án đúng là: <span className="text-green-600">{section.answer}</span>
                                    </p>
                                )}
                            </motion.div>
                        )}
                    </div>
                );
            case "exercise":
                return (
                    <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                        <div className="flex items-center mb-4">
                            <svg className="w-6 h-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <h3 className="text-lg font-semibold text-green-800">Bài tập thực hành</h3>
                        </div>
                        <div className="mb-6">
                            {isMarkdown ? (
                                <MarkdownRenderer
                                    content={content}
                                    className="prose-green"
                                />
                            ) : isHtml ? (
                                <div className="prose prose-green max-w-none">
                                    <div dangerouslySetInnerHTML={{ __html: content }} />
                                </div>
                            ) : (
                                <div className="prose prose-green max-w-none">
                                    <p className="text-green-900 leading-relaxed whitespace-pre-wrap">{content}</p>
                                </div>
                            )}
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-green-200">
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-sm font-medium text-green-700">💡 Gợi ý:</span>
                                <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">Thực hành</span>
                            </div>
                            <p className="text-sm text-green-700">
                                Hãy thử thực hiện bài tập này để củng cố kiến thức vừa học. Bạn có thể sử dụng môi trường lập trình yêu thích của mình.
                            </p>
                        </div>
                    </div>
                );
            default:
                return (
                    <div className="bg-gray-100 p-4 rounded-lg border border-gray-300 text-center">
                        <p className="text-gray-600">Không hỗ trợ loại nội dung: <span className="font-mono">{section.type}</span></p>
                    </div>
                );
        }
    };

    return (
        <div className="min-h-screen pb-20">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center mb-2">
                        <Link href={`/topics/${lesson.topicId}`} className="text-primary hover:underline">
                            {`Chủ đề ${lesson.order}`}
                        </Link>
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

                            <Link
                                href={`/topics/${lesson.topicId}`}
                                className="px-6 py-3 bg-accent text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all"
                            >
                                Quay lại chủ đề
                            </Link>
                            {nextLessonId ? (
                                <Link
                                    href={`/lessons/${nextLessonId}`}
                                    className="px-6 py-3 bg-primary text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all"
                                >
                                    Bắt đầu bài học tiếp theo
                                </Link>
                            ) : (
                                <Link
                                    href={`#`}
                                    className="px-6 bg-gray-100 py-3 text-gray-400 font-semibold rounded-lg shadow-md hover:shadow-lg transition-all"
                                >
                                    Bắt đầu bài học tiếp theo
                                </Link>
                            )}
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
                        {renderSection(currentSection as any)}

                        <div className="flex justify-between mt-8">
                            {currentSectionIndex > 0 ? (
                                <button
                                    onClick={handlePrev}
                                    className={`px-4 py-2 rounded-lg ${currentSectionIndex === 0
                                        ? "text-gray-400 cursor-not-allowed"
                                        : "bg-foreground/15"
                                        }`}
                                >
                                    Quay lại
                                </button>
                            ) : <div></div>}
                            <button
                                onClick={handleNext}
                                disabled={isQuiz && (selectedAnswer === null || selectedAnswer !== currentSection.answer)}
                                className={`px-6 py-2 rounded-lg ${isQuiz && (selectedAnswer === null || selectedAnswer !== currentSection.answer)
                                    ? "bg-gray-400 text-white cursor-not-allowed"
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
                    {lesson.sections.map((_, index: number) => (
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
