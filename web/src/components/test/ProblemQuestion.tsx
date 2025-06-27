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
    onSubmit: (answer: string) => Promise<void>;
    isSubmitting: boolean;
    feedback?: { isCorrect: boolean; feedback?: string };
    initialAnswer?: string;
}

export const ProblemQuestion: React.FC<ProblemQuestionProps> = ({
    question,
    onSubmit,
    isSubmitting,
    feedback,
    initialAnswer
}) => {
    const [answer, setAnswer] = useState<string>(initialAnswer || '');
    const [hasSubmitted, setHasSubmitted] = useState<boolean>(!!feedback || !!initialAnswer);

    useEffect(() => {
        setAnswer(initialAnswer || '');
        setHasSubmitted(!!feedback || !!initialAnswer);
    }, [question.id, initialAnswer, feedback]);

    const handleSubmit = async () => {
        if (!answer.trim()) return;

        try {
            await onSubmit(answer);
            setHasSubmitted(true);
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    };

    const handleAnswerChange = (value: string) => {
        setAnswer(value);
    };

    const handleEdit = () => {
        setHasSubmitted(false);
    };

    // Determine if answer is correct (for essay questions, this might be based on feedback)
    const isCorrect = feedback?.isCorrect;
    const showAnswer = hasSubmitted || feedback;

    return (
        <Paper p="lg" withBorder>
            <Stack gap="md">
                {/* Question header */}
                <Group justify="space-between" align="flex-start">
                    <div style={{ flex: 1 }}>
                        <Title order={4} mb="xs">Câu hỏi tự luận</Title>
                        <Text>{question.content}</Text>
                    </div>
                    <Group gap="xs">
                        {question.difficulty && (
                            <Badge color="orange" variant="light" size="sm">
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
                        disabled={hasSubmitted && isSubmitting}
                        styles={{
                            input: {
                                backgroundColor: hasSubmitted ? '#f8f9fa' : undefined,
                                borderColor: showAnswer && isCorrect ? '#28a745' :
                                    showAnswer && isCorrect === false ? '#ffc107' : undefined
                            }
                        }}
                    />
                    <Text size="xs" c="dimmed">
                        {answer.length} ký tự
                    </Text>
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

                {/* Action buttons */}
                <Group justify="flex-end">
                    {!hasSubmitted ? (
                        <Button
                            onClick={handleSubmit}
                            disabled={!answer.trim() || isSubmitting}
                            loading={isSubmitting}
                            color="blue"
                        >
                            {isSubmitting ? 'Đang lưu...' : 'Lưu câu trả lời'}
                        </Button>
                    ) : (
                        <Group>
                            <Button
                                variant="outline"
                                leftSection={<IconEdit size={16} />}
                                onClick={handleEdit}
                                disabled={isSubmitting}
                            >
                                Chỉnh sửa
                            </Button>
                            {!hasSubmitted && (
                                <Button
                                    onClick={handleSubmit}
                                    disabled={!answer.trim() || isSubmitting}
                                    loading={isSubmitting}
                                    color="blue"
                                >
                                    Lưu lại
                                </Button>
                            )}
                        </Group>
                    )}
                </Group>

                {hasSubmitted && !isSubmitting && (
                    <Alert color="blue" variant="light">
                        <Text size="sm">
                            ✅ Câu trả lời của bạn đã được lưu. Bạn có thể tiếp tục với câu hỏi tiếp theo hoặc chỉnh sửa câu trả lời này.
                        </Text>
                    </Alert>
                )}
            </Stack>
        </Paper>
    );
};

export default ProblemQuestion; 