import React, { useState, useEffect } from 'react';
import { Paper, Title, Text, Stack, Textarea, Button, Alert, Badge, Group } from '@mantine/core';
import { IconCheck, IconX, IconAlertCircle, IconEdit } from '@tabler/icons-react';

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

    useEffect(() => {
        setAnswer(initialAnswer || '');
    }, [question.id, initialAnswer]);

    const handleAnswerChange = (value: string) => {
        setAnswer(value);
        // Gọi callback ngay lập tức - useTestSession sẽ xử lý debounce
        onAnswerChange(value);
    };

    const handleEdit = () => {
        setAnswer(initialAnswer || '');
    };

    // Determine if answer is correct (for essay questions, this might be based on feedback)
    const isCorrect = feedback?.isCorrect;
    const showAnswer = !!feedback;

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
                                    showAnswer && isCorrect === false ? '#ffc107' : undefined
                            }
                        }}
                    />
                    <Group justify="space-between">
                        <Text size="xs" c="dimmed">
                            {answer.length} ký tự
                        </Text>
                        <Text size="xs" c="green">
                            ✅ Tự động lưu
                        </Text>
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