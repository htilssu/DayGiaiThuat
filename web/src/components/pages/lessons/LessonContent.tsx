'use client';

import React from 'react';
import LessonSection from './LessonSection';

interface LessonSectionData {
    type: 'text' | 'code' | 'quiz' | string;
    content: string;
    options?: Record<string, string>;
    answer?: string;
    explanation?: string;
    language?: string;
}

interface LessonContentProps {
    sections: LessonSectionData[];
    className?: string;
}

/**
 * Component hiển thị toàn bộ nội dung bài học
 */
export const LessonContent: React.FC<LessonContentProps> = ({
    sections,
    className = ''
}) => {
    if (!sections || sections.length === 0) {
        return (
            <div className={`text-center py-12 ${className}`}>
                <div className="text-6xl mb-4">📚</div>
                <h3 className="text-xl font-semibold text-foreground mb-2">
                    Chưa có nội dung bài học
                </h3>
                <p className="text-muted-foreground">
                    Nội dung bài học đang được cập nhật. Vui lòng quay lại sau.
                </p>
            </div>
        );
    }

    return (
        <div className={`space-y-6 ${className}`}>
            {sections.map((section, index) => (
                <LessonSection
                    key={index}
                    section={section}
                    index={index}
                    className="animate-in fade-in-50 duration-500"
                    style={{
                        animationDelay: `${index * 100}ms`
                    }}
                />
            ))}

            {/* Footer của bài học */}
            <div className="mt-8 p-6 bg-primary/5 rounded-xl border border-primary/20">
                <div className="flex items-center gap-3 mb-3">
                    <span className="text-2xl">🎓</span>
                    <h3 className="text-lg font-semibold text-foreground">
                        Hoàn thành bài học
                    </h3>
                </div>
                <p className="text-muted-foreground mb-4">
                    Bạn đã hoàn thành bài học này! Hãy tiếp tục với bài học tiếp theo để nâng cao kiến thức.
                </p>
                <div className="flex gap-3">
                    <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors">
                        Bài học tiếp theo
                    </button>
                    <button className="px-4 py-2 border border-foreground/20 text-foreground rounded-lg hover:bg-foreground/5 transition-colors">
                        Quay lại danh sách
                    </button>
                </div>
            </div>
        </div>
    );
};

export default LessonContent; 