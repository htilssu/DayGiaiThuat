"use client";

import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { Topic, topicsData } from "./topicsData";

interface TopicCardProps {
    topic: Topic;
    index: number;
    isExpanded: boolean;
    toggleExpand: () => void;
}

export function TopicCard({ topic, index, isExpanded, toggleExpand }: TopicCardProps) {
    return (
        <div className="relative">
            {/* Chủ đề */}
            <div
                className={`relative z-10 flex items-start gap-4 p-4 rounded-xl border transition-all ${topic.isLocked
                        ? "bg-foreground/5 border-foreground/10 opacity-70"
                        : "bg-white border-foreground/10 shadow-sm hover:shadow"
                    }`}
            >
                {/* Icon và trạng thái */}
                <div className="relative">
                    <div
                        className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${topic.isLocked
                                ? "bg-foreground/20 text-foreground/50"
                                : `bg-${topic.color} text-white`
                            }`}
                    >
                        {topic.isLocked ? "🔒" : topic.icon}
                    </div>
                    {!topic.isLocked && topic.completedLessons > 0 && (
                        <div className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-green-500 text-white text-xs flex items-center justify-center">
                            {topic.completedLessons}
                        </div>
                    )}
                </div>

                {/* Nội dung chủ đề */}
                <div className="flex-1">
                    <div className="flex items-center justify-between">
                        <h3 className="text-xl font-semibold">{topic.title}</h3>
                        {!topic.isLocked && (
                            <Link
                                href={`/topics/${topic.id}`}
                                className="text-primary hover:underline text-sm"
                            >
                                Xem chi tiết
                            </Link>
                        )}
                    </div>
                    <p className="text-foreground/70 text-sm mt-1">{topic.description}</p>

                    {/* Thanh tiến độ */}
                    {!topic.isLocked && (
                        <div className="mt-3">
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span>Tiến độ: {topic.completedLessons}/{topic.totalLessons} bài học</span>
                                <span>{topic.progress}%</span>
                            </div>
                            <div className="w-full bg-foreground/10 rounded-full h-2 overflow-hidden">
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${topic.progress}%` }}
                                    transition={{ duration: 1, delay: index * 0.2 }}
                                    className={`h-2 rounded-full bg-${topic.color}`}
                                ></motion.div>
                            </div>
                        </div>
                    )}

                    {/* Điều kiện tiên quyết */}
                    {topic.isLocked && topic.prerequisites && topic.prerequisites.length > 0 && (
                        <div className="mt-3 text-sm">
                            <p className="text-foreground/60">
                                Để mở khóa, hoàn thành:
                                {topic.prerequisites.map((prereqId, i) => {
                                    const prereq = topicsData.find((t) => t.id === prereqId);
                                    return (
                                        <span key={prereqId}>
                                            {i > 0 && ", "}
                                            <span className="font-medium">{prereq?.title}</span>
                                        </span>
                                    );
                                })}
                            </p>
                        </div>
                    )}

                    {/* Nút mở rộng danh sách bài học */}
                    {!topic.isLocked && topic.lessons && topic.lessons.length > 0 && (
                        <button
                            onClick={toggleExpand}
                            className="mt-3 text-sm flex items-center text-primary"
                        >
                            {isExpanded ? "Ẩn bài học" : "Xem bài học"}
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                className={`h-4 w-4 ml-1 transition-transform ${isExpanded ? "rotate-180" : ""
                                    }`}
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M19 9l-7 7-7-7"
                                />
                            </svg>
                        </button>
                    )}
                </div>
            </div>

            {/* Danh sách bài học */}
            <AnimatePresence>
                {!topic.isLocked && isExpanded && topic.lessons && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden"
                    >
                        <div className="pl-14 pr-4 mt-2 space-y-2">
                            {topic.lessons.map((lesson) => (
                                <Link
                                    key={lesson.id}
                                    href={`/topics/${topic.id}/lessons/${lesson.id}`}
                                    className={`flex items-center p-3 rounded-lg border transition-all ${lesson.isCompleted
                                            ? "bg-green-50 border-green-200"
                                            : "bg-white border-foreground/10 hover:border-primary/30"
                                        }`}
                                >
                                    <div
                                        className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${lesson.isCompleted
                                                ? "bg-green-500 text-white"
                                                : "bg-foreground/10"
                                            }`}
                                    >
                                        {lesson.isCompleted ? (
                                            <svg
                                                xmlns="http://www.w3.org/2000/svg"
                                                className="h-4 w-4"
                                                fill="none"
                                                viewBox="0 0 24 24"
                                                stroke="currentColor"
                                            >
                                                <path
                                                    strokeLinecap="round"
                                                    strokeLinejoin="round"
                                                    strokeWidth={2}
                                                    d="M5 13l4 4L19 7"
                                                />
                                            </svg>
                                        ) : (
                                            lesson.id
                                        )}
                                    </div>
                                    <span className={lesson.isCompleted ? "text-green-800" : ""}>
                                        {lesson.title}
                                    </span>
                                </Link>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
} 