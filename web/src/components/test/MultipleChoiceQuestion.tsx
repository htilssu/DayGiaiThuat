import React, { useState, useEffect } from 'react';
import { Radio, Stack, Button, Text, Paper, Box } from '@mantine/core';
import { TestQuestion } from '@/lib/api';

interface MultipleChoiceQuestionProps {
    question: TestQuestion;
    onSubmit: (selectedOptionId: string) => Promise<void>;
    isSubmitting?: boolean;
    selectedOptionId?: string;
    feedback?: {
        isCorrect: boolean;
        feedback?: string;
    };
}

export const MultipleChoiceQuestion: React.FC<MultipleChoiceQuestionProps> = ({
    question,
    onSubmit,
    isSubmitting = false,
    selectedOptionId,
    feedback,
}) => {
    const [selectedOption, setSelectedOption] = useState<string | undefined>(selectedOptionId);
    const [isAnswerSubmitted, setIsAnswerSubmitted] = useState(!!feedback);

    // Update selected option when prop changes
    useEffect(() => {
        if (selectedOptionId) {
            setSelectedOption(selectedOptionId);
        }
    }, [selectedOptionId]);

    // Set answer as submitted when feedback is provided
    useEffect(() => {
        if (feedback) {
            setIsAnswerSubmitted(true);
        }
    }, [feedback]);

    const handleSubmit = async () => {
        if (!selectedOption) return;

        await onSubmit(selectedOption);
        setIsAnswerSubmitted(true);
    };

    return (
        <Paper p="md" withBorder>
            <Stack>
                <Text fw={600} size="lg">{question.title}</Text>
                <Text>{question.content}</Text>

                <Radio.Group
                    value={selectedOption}
                    onChange={setSelectedOption}
                    name={`question-${question.id}`}
                >
                    <Stack>
                        {question.options?.map((option) => (
                            <Radio
                                key={option.id}
                                value={option.id}
                                label={option.text}
                                disabled={isAnswerSubmitted}
                            />
                        ))}
                    </Stack>
                </Radio.Group>

                {feedback && (
                    <Box
                        p="sm"
                        bg={feedback.isCorrect ? 'green.1' : 'red.1'}
                        c={feedback.isCorrect ? 'green.8' : 'red.8'}
                        style={{ borderRadius: '4px' }}
                    >
                        <Text fw={500}>
                            {feedback.isCorrect ? 'Đúng!' : 'Sai!'}
                        </Text>
                        {feedback.feedback && (
                            <Text size="sm" mt="xs">{feedback.feedback}</Text>
                        )}
                    </Box>
                )}

                <Button
                    onClick={handleSubmit}
                    disabled={!selectedOption || isAnswerSubmitted}
                    loading={isSubmitting}
                >
                    Nộp câu trả lời
                </Button>
            </Stack>
        </Paper>
    );
};

export default MultipleChoiceQuestion; 