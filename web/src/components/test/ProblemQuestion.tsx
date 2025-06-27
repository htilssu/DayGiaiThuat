import React, { useState, useEffect } from 'react';
import { Paper, Title, Text, Stack, Textarea, Button, Alert, Badge, Group } from '@mantine/core';
import { IconCheck, IconX, IconAlertCircle, IconEdit } from '@tabler/icons-react';
import { useDebouncedCallback } from '@mantine/hooks';

export interface TestQuestion {
    id: string;
    content: string;
    type: 'single_choice' | 'essay';
    difficulty?: string;
    answer?: string;
    options?: string[];
}

interface ProblemQuestionProps {
    question: TestQuestion;
    onAnswerChange: (answer: string) => void;
    feedback?: { isCorrect: boolean; feedback?: string };
    initialAnswer?: string;
    questionNumber?: number;
}

export const ProblemQuestion: React.FC<ProblemQuestionProps> = ({
    question,
    onAnswerChange,
    feedback,
    initialAnswer,
    questionNumber
}) => {
    const [answer, setAnswer] = useState<string>(initialAnswer || '');
    const [lastSavedAnswer, setLastSavedAnswer] = useState<string>(initialAnswer || '');

    useEffect(() => {
        setAnswer(initialAnswer || '');
        setLastSavedAnswer(initialAnswer || '');
    }, [question.id, initialAnswer]);

    // Debounced function để tự động gửi qua socket sau 1 giây khi user ngừng typing
    const debouncedSave = useDebouncedCallback((value: string) => {
        if (value !== lastSavedAnswer) {
            onAnswerChange(value); // Gửi qua socket thông qua callback
            setLastSavedAnswer(value);
        }
    }, 1000);

    const handleAnswerChange = (value: string) => {
        setAnswer(value);
        // Gọi debounced save
        debouncedSave(value);
    };

    const handleEdit = () => {
        setAnswer(initialAnswer || '');
        setLastSavedAnswer(initialAnswer || '');
    };

    // Determine if answer is correct (for essay questions, this might be based on feedback)
    const isCorrect = feedback?.isCorrect;
    const showAnswer = !!feedback;
    const hasUnsavedChanges = answer !== lastSavedAnswer;

    return (
        <Paper p="lg" withBorder>
            <Stack gap="md">
                {/* Question header */}
                <Group justify="space-between" align="flex-start">
                    <div style={{ flex: 1 }}>
                        <Group gap="xs" mb="xs">
                            {questionNumber && (
                                <Badge color="blue" variant="filled" size="sm">
                                    Câu {questionNumber}
                                </Badge>
                            )}
                            <Badge color="orange" variant="light" size="sm">
                                Tự luận
                            </Badge>
                        </Group>
                        <Text>{question.content}</Text>
                    </div>
                    <Group gap="xs">
                        {question.difficulty && (
                            <Badge color="gray" variant="light" size="sm">
                                {question.difficulty}
                            </Badge>
                        )}
                        {showAnswer && feedback?.isCorrect !== undefined && (
                            <Badge
                                color={isCorrect ? 'green' : 'orange'}
                                variant="filled"
                                size="sm"
                                leftSection={isCorrect ? <IconCheck size={12} /> : <IconX size={12} />}
                            >
                                {isCorrect ? 'Đạt yêu cầu' : 'Cần cải thiện'}
                            </Badge>
                        )}
                    </Group>
                </Group>

                {/* Answer input */}
                <Stack gap="sm">
                    <Text size="sm" fw={500}>Câu trả lời của bạn:</Text>
                    <Textarea
                        value={answer}
                        onChange={(event) => handleAnswerChange(event.currentTarget.value)}
                        placeholder="Nhập câu trả lời của bạn..."
                        minRows={6}
                        maxRows={15}
                        autosize
                        styles={{
                            input: {
                                borderColor: showAnswer && isCorrect ? '#28a745' :
                                    showAnswer && isCorrect === false ? '#ffc107' :
                                        hasUnsavedChanges ? '#1890ff' : undefined
                            }
                        }}
                    />
                    <Group justify="space-between">
                        <Text size="xs" c="dimmed">
                            {answer.length} ký tự
                        </Text>
                        {hasUnsavedChanges && (
                            <Text size="xs" c="blue">
                                Đang lưu...
                            </Text>
                        )}
                        {!hasUnsavedChanges && lastSavedAnswer && (
                            <Text size="xs" c="green">
                                ✅ Đã lưu
                            </Text>
                        )}
                    </Group>
                </Stack>

                {/* Feedback */}
                {showAnswer && feedback?.feedback && (
                    <Alert
                        icon={<IconAlertCircle size="1rem" />}
                        title="Phản hồi từ hệ thống"
                        color={isCorrect ? 'green' : 'orange'}
                        variant="light"
                    >
                        {feedback.feedback}
                    </Alert>
                )}

                {/* Show suggested answer if available */}
                {showAnswer && question.answer && (
                    <Alert
                        icon={<IconCheck size="1rem" />}
                        title="Gợi ý đáp án"
                        color="blue"
                        variant="light"
                    >
                        <Text size="sm">
                            <strong>Gợi ý:</strong> {question.answer}
                        </Text>
                    </Alert>
                )}

            </Stack>
        </Paper>
    );
};

export default ProblemQuestion; 