import React, { useState, useEffect } from 'react';
import { Paper, Title, Text, Stack, Radio, Button, Alert, Badge, Group } from '@mantine/core';
import { IconCheck, IconX, IconAlertCircle } from '@tabler/icons-react';

export interface TestQuestion {
    id: string;
    content: string;
    type: 'single_choice' | 'essay';
    difficulty?: string;
    answer?: string;
    options?: string[];
}

interface MultipleChoiceQuestionProps {
    question: TestQuestion;
    onSubmit: (selectedOption: string) => Promise<void>;
    isSubmitting: boolean;
    feedback?: { isCorrect: boolean; feedback?: string };
    initialAnswer?: string;
}

// Utility function to shuffle array
const shuffleArray = <T,>(array: T[]): T[] => {
    const newArray = [...array];
    for (let i = newArray.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
    }
    return newArray;
};

export const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
    question,
    onSubmit,
    isSubmitting,
    feedback,
    initialAnswer
}) => {
    const [selectedOption, setSelectedOption] = useState<string>(initialAnswer || '');
    const [shuffledOptions, setShuffledOptions] = useState<string[]>([]);
    const [hasSubmitted, setHasSubmitted] = useState<boolean>(!!feedback);

    // Initialize shuffled options on mount or when question changes
    useEffect(() => {
        if (question.options && question.options.length > 0) {
            // Only shuffle if we don't have a previous answer (to maintain consistency)
            if (!initialAnswer && !feedback) {
                setShuffledOptions(shuffleArray(question.options));
            } else {
                setShuffledOptions(question.options);
            }
        }
        setSelectedOption(initialAnswer || '');
        setHasSubmitted(!!feedback);
    }, [question.id, question.options, initialAnswer, feedback]);

    const handleSubmit = async () => {
        if (!selectedOption) return;

        try {
            await onSubmit(selectedOption);
            setHasSubmitted(true);
        } catch (error) {
            console.error('Error submitting answer:', error);
        }
    };

    const handleOptionChange = (value: string) => {
        if (!hasSubmitted) {
            setSelectedOption(value);
        }
    };

    // Determine if answer is correct
    const isCorrect = feedback?.isCorrect ?? (hasSubmitted && selectedOption === question.answer);
    const showAnswer = hasSubmitted || feedback;

    return (
        <Paper p="lg" withBorder>
            <Stack gap="md">
                {/* Question header */}
                <Group justify="space-between" align="flex-start">
                    <div style={{ flex: 1 }}>
                        <Title order={4} mb="xs">Câu hỏi trắc nghiệm</Title>
                        <Text>{question.content}</Text>
                    </div>
                    <Group gap="xs">
                        {question.difficulty && (
                            <Badge color="blue" variant="light" size="sm">
                                {question.difficulty}
                            </Badge>
                        )}
                        {showAnswer && (
                            <Badge
                                color={isCorrect ? 'green' : 'red'}
                                variant="filled"
                                size="sm"
                                leftSection={isCorrect ? <IconCheck size={12} /> : <IconX size={12} />}
                            >
                                {isCorrect ? 'Đúng' : 'Sai'}
                            </Badge>
                        )}
                    </Group>
                </Group>

                {/* Options */}
                <Radio.Group
                    value={selectedOption}
                    onChange={handleOptionChange}
                    label="Chọn đáp án đúng:"
                    size="md"
                >
                    <Stack gap="sm" mt="sm">
                        {shuffledOptions.map((option, index) => {
                            const isSelectedOption = selectedOption === option;
                            const isCorrectOption = showAnswer && option === question.answer;
                            const isWrongSelection = showAnswer && isSelectedOption && !isCorrectOption;

                            return (
                                <Paper
                                    key={`${question.id}-option-${index}`}
                                    p="sm"
                                    withBorder
                                    style={{
                                        backgroundColor: isCorrectOption
                                            ? '#e8f5e8'
                                            : isWrongSelection
                                                ? '#ffe8e8'
                                                : undefined,
                                        borderColor: isCorrectOption
                                            ? '#28a745'
                                            : isWrongSelection
                                                ? '#dc3545'
                                                : undefined,
                                        cursor: hasSubmitted ? 'default' : 'pointer'
                                    }}
                                >
                                    <Radio
                                        value={option}
                                        label={
                                            <Group gap="xs" wrap="nowrap">
                                                <Text size="sm">{option}</Text>
                                                {isCorrectOption && showAnswer && (
                                                    <IconCheck size={16} color="green" />
                                                )}
                                                {isWrongSelection && (
                                                    <IconX size={16} color="red" />
                                                )}
                                            </Group>
                                        }
                                        disabled={hasSubmitted}
                                        styles={{
                                            radio: {
                                                cursor: hasSubmitted ? 'default' : 'pointer'
                                            },
                                            label: {
                                                cursor: hasSubmitted ? 'default' : 'pointer'
                                            }
                                        }}
                                    />
                                </Paper>
                            );
                        })}
                    </Stack>
                </Radio.Group>

                {/* Feedback */}
                {showAnswer && feedback?.feedback && (
                    <Alert
                        icon={<IconAlertCircle size="1rem" />}
                        title="Giải thích"
                        color={isCorrect ? 'green' : 'orange'}
                        variant="light"
                    >
                        {feedback.feedback}
                    </Alert>
                )}

                {/* Show correct answer if submitted and got it wrong */}
                {showAnswer && !isCorrect && question.answer && (
                    <Alert
                        icon={<IconCheck size="1rem" />}
                        title="Đáp án đúng"
                        color="green"
                        variant="light"
                    >
                        <Text size="sm">
                            <strong>Đáp án đúng:</strong> {question.answer}
                        </Text>
                    </Alert>
                )}

                {/* Submit button */}
                {!hasSubmitted && (
                    <Group justify="flex-end">
                        <Button
                            onClick={handleSubmit}
                            disabled={!selectedOption || isSubmitting}
                            loading={isSubmitting}
                            color="blue"
                        >
                            {isSubmitting ? 'Đang lưu...' : 'Lưu câu trả lời'}
                        </Button>
                    </Group>
                )}

                {hasSubmitted && (
                    <Alert color="blue" variant="light">
                        <Text size="sm">
                            ✅ Câu trả lời của bạn đã được lưu. Bạn có thể tiếp tục với câu hỏi tiếp theo.
                        </Text>
                    </Alert>
                )}
            </Stack>
        </Paper>
    );
};

export default MultipleChoiceQuestion; 