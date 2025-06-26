import React, { useState, useEffect } from 'react';
import { Stack, Button, Text, Paper, Box, Tabs } from '@mantine/core';
import Editor from '@monaco-editor/react';
import { TestQuestion } from '@/lib/api';

interface ProblemQuestionProps {
    question: TestQuestion;
    onSubmit: (code: string) => Promise<void>;
    isSubmitting?: boolean;
    initialCode?: string;
    feedback?: {
        isCorrect: boolean;
        feedback?: string;
    };
}

export const ProblemQuestion: React.FC<ProblemQuestionProps> = ({
    question,
    onSubmit,
    isSubmitting = false,
    initialCode,
    feedback,
}) => {
    const [code, setCode] = useState<string>(initialCode || question.codeTemplate || '');
    const [isAnswerSubmitted, setIsAnswerSubmitted] = useState(!!feedback);

    // Update code when initialCode prop changes
    useEffect(() => {
        if (initialCode) {
            setCode(initialCode);
        }
    }, [initialCode]);

    // Set answer as submitted when feedback is provided
    useEffect(() => {
        if (feedback) {
            setIsAnswerSubmitted(true);
        }
    }, [feedback]);

    const handleEditorChange = (value: string | undefined) => {
        if (value !== undefined) {
            setCode(value);
        }
    };

    const handleSubmit = async () => {
        await onSubmit(code);
        setIsAnswerSubmitted(true);
    };

    return (
        <Paper p="md" withBorder>
            <Stack>
                <Text fw={600} size="lg">{question.title}</Text>

                <Tabs defaultValue="problem">
                    <Tabs.List>
                        <Tabs.Tab value="problem">Đề bài</Tabs.Tab>
                        <Tabs.Tab value="solution">Giải pháp</Tabs.Tab>
                    </Tabs.List>

                    <Tabs.Panel value="problem" pt="md">
                        <Text>{question.content}</Text>
                    </Tabs.Panel>

                    <Tabs.Panel value="solution" pt="md">
                        <Box h={400}>
                            <Editor
                                height="100%"
                                defaultLanguage="python"
                                value={code}
                                onChange={handleEditorChange}
                                options={{
                                    minimap: { enabled: false },
                                    scrollBeyondLastLine: false,
                                    fontSize: 14,
                                    readOnly: isAnswerSubmitted,
                                }}
                            />
                        </Box>
                    </Tabs.Panel>
                </Tabs>

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
                    disabled={isAnswerSubmitted}
                    loading={isSubmitting}
                >
                    Nộp bài
                </Button>
            </Stack>
        </Paper>
    );
};

export default ProblemQuestion; 