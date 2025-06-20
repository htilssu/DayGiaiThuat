import { client } from "./client";

export interface TestQuestion {
    id: string;
    title: string;
    content: string;
    type: "multiple_choice" | "problem";
    options?: {
        id: string;
        text: string;
    }[];
    codeTemplate?: string;
}

export interface Test {
    id: string;
    title: string;
    description: string;
    duration: number;
    topicId?: string;
    questions: TestQuestion[];
}

export interface TestSubmission {
    testId: string;
    answers: {
        questionId: string;
        selectedOptionId?: string;
        code?: string;
    }[];
}

export interface TestResult {
    score: number;
    totalQuestions: number;
    correctAnswers: number;
    feedback: {
        questionId: string;
        isCorrect: boolean;
        feedback?: string;
    }[];
}

export const testApi = {
    getTests: async (): Promise<Test[]> => {
        const response = await client.get('/tests');
        return response.data;
    },

    getTest: async (testId: string): Promise<Test> => {
        const response = await client.get(`/tests/${testId}`);
        return response.data;
    },

    getTestByTopic: async (topicId: string): Promise<Test | null> => {
        try {
            const response = await client.get(`/tests/topic/${topicId}`);
            return response.data;
        } catch (error) {
            console.error("Error fetching test for topic:", error);
            return null;
        }
    },

    submitTest: async (submission: TestSubmission): Promise<TestResult> => {
        const response = await client.post(`/tests/${submission.testId}/submit`, submission);
        return response.data;
    },

    submitQuestion: async (testId: string, questionId: string, answer: { selectedOptionId?: string; code?: string }): Promise<{ isCorrect: boolean; feedback?: string }> => {
        const response = await client.post(`/tests/${testId}/questions/${questionId}/submit`, answer);
        return response.data;
    }
}; 