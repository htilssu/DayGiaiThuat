"use client";

import { useState } from "react";
import { TopicCard } from "./TopicCard";
import { topicsData } from "./topicsData";

export function LearningRoadmap() {
    const [expandedTopics, setExpandedTopics] = useState<string[]>([]);

    const toggleTopic = (topicId: string) => {
        if (expandedTopics.includes(topicId)) {
            setExpandedTopics(expandedTopics.filter((id) => id !== topicId));
        } else {
            setExpandedTopics([...expandedTopics, topicId]);
        }
    };

    const isTopicExpanded = (topicId: string) => expandedTopics.includes(topicId);

    return (
        <div className="max-w-3xl mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold mb-2">Lộ trình học tập</h1>
            <p className="text-foreground/70 mb-8">
                Theo dõi tiến trình và hoàn thành các chủ đề để mở khóa nội dung mới
            </p>

            <div className="relative">
                {/* Đường kẻ dọc kết nối các chủ đề */}
                <div className="absolute left-5 top-8 bottom-8 w-0.5 bg-foreground/10"></div>

                {/* Danh sách các chủ đề */}
                <div className="space-y-6">
                    {topicsData.map((topic, index) => (
                        <TopicCard
                            key={topic.id}
                            topic={topic}
                            index={index}
                            isExpanded={isTopicExpanded(topic.id)}
                            toggleExpand={() => toggleTopic(topic.id)}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}
