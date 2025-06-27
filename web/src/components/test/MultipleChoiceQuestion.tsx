import React, { useState, useEffect } from 'react';
import { Paper, Title, Text, Stack, Radio, Alert, Badge, Group } from '@mantine/core';
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
    onAnswerChange: (selectedOption: string) => void;
    feedback?: { isCorrect: boolean; feedback?: string };
    initialAnswer?: string;
    questionNumber?: number;
}


export const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
    question,
    onAnswerChange,
    feedback,
    initialAnswer,
    questionNumber
}) => {
    const [selectedOption, setSelectedOption] = useState<string>(initialAnswer || '');

    // Initialize selected answer when question or initial answer changes
    useEffect(() => {
        setSelectedOption(initialAnswer || '');
    }, [question.id, initialAnswer]);

    const handleOptionChange = (value: string) => {
        setSelectedOption(value);
        // Tự động gửi qua socket ngay khi user thay đổi (thông qua onAnswerChange callback)
        onAnswerChange(value);
    };

    // Determine if answer is correct
    const isCorrect = feedback?.isCorrect ?? (selectedOption === question.answer && !!selectedOption);
    const showAnswer = !!feedback;

    // Use original options order - không trộn câu trả lời
    const displayOptions = question.options || [];

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
                            <Badge color="cyan" variant="light" size="sm">
                                Trắc nghiệm
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
                        {displayOptions.map((option, index) => {
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
                                                : isSelectedOption
                                                    ? '#e6f3ff'
                                                    : undefined,
                                        borderColor: isCorrectOption
                                            ? '#28a745'
                                            : isWrongSelection
                                                ? '#dc3545'
                                                : isSelectedOption
                                                    ? '#1890ff'
                                                    : undefined,
                                        cursor: 'pointer'
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
                                        styles={{
                                            radio: {
                                                cursor: 'pointer'
                                            },
                                            label: {
                                                cursor: 'pointer'
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


            </Stack>
        </Paper>
    );
};

export default MultipleChoiceQuestion; 