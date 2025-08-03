'use client';

import React, { useState } from 'react';
import { ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';

interface CodeSectionProps {
    content: string;
    language?: string;
    title?: string;
    showLineNumbers?: boolean;
    className?: string;
}

/**
 * Component hiển thị code với tính năng copy và syntax highlighting
 */
export const CodeSection: React.FC<CodeSectionProps> = ({
    content,
    language = 'javascript',
    title = 'Ví dụ mã nguồn',
    showLineNumbers = true,
    className = ''
}) => {
    const [copied, setCopied] = useState(false);

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    const formatCodeWithLineNumbers = (code: string) => {
        const lines = code.split('\n');
        return lines.map((line, index) => (
            <div key={index} className="flex">
                {showLineNumbers && (
                    <span className="text-slate-500 text-xs w-8 text-right mr-4 select-none">
                        {index + 1}
                    </span>
                )}
                <span className="flex-1">{line}</span>
            </div>
        ));
    };

    const getLanguageIcon = () => {
        switch (language.toLowerCase()) {
            case 'javascript':
            case 'js':
                return '🟨';
            case 'python':
            case 'py':
                return '🐍';
            case 'java':
                return '☕';
            case 'html':
                return '🌐';
            case 'css':
                return '🎨';
            case 'react':
            case 'jsx':
            case 'tsx':
                return '⚛️';
            default:
                return '💻';
        }
    };

    return (
        <div className={`${className}`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                    <span className="text-2xl">{getLanguageIcon()}</span>
                    {title}
                    {language && (
                        <span className="text-xs px-2 py-1 bg-foreground/10 text-foreground/60 rounded uppercase">
                            {language}
                        </span>
                    )}
                </h3>

                <button
                    onClick={handleCopy}
                    className="flex items-center gap-2 px-3 py-1.5 text-xs bg-foreground/5 hover:bg-foreground/10 text-foreground/70 hover:text-foreground rounded-lg transition-all"
                    title="Copy code"
                >
                    {copied ? (
                        <>
                            <CheckIcon className="h-4 w-4 text-green-500" />
                            <span className="text-green-500">Đã copy!</span>
                        </>
                    ) : (
                        <>
                            <ClipboardIcon className="h-4 w-4" />
                            <span>Copy</span>
                        </>
                    )}
                </button>
            </div>

            {/* Code Block */}
            <div className="relative">
                <div className="bg-slate-900 dark:bg-slate-800 rounded-lg p-4 overflow-x-auto border">
                    <pre className="text-sm font-mono text-green-400 leading-relaxed">
                        <code>{formatCodeWithLineNumbers(content)}</code>
                    </pre>
                </div>

                {/* Gradient overlay for long code */}
                <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-slate-900 to-transparent pointer-events-none rounded-b-lg" />
            </div>

            {/* Tips */}
            <div className="mt-3 flex items-start gap-2 text-xs text-muted-foreground">
                <span className="text-base">💡</span>
                <div>
                    <p className="font-medium">Mẹo học tập:</p>
                    <ul className="mt-1 space-y-1">
                        <li>• Hãy đọc từng dòng code và hiểu ý nghĩa</li>
                        <li>• Copy code này và thử chạy trong IDE của bạn</li>
                        <li>• Thử thay đổi một số giá trị để xem kết quả khác nhau</li>
                    </ul>
                </div>
            </div>
        </div>
    );
};

export default CodeSection; 