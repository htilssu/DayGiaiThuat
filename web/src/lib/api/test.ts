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
    topicId?: number;
    courseId?: number;
    duration_minutes: number;
    questions: Record<string, any>;
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

export interface TestAnswer {
    selectedOptionId?: string;
    code?: string;
    [key: string]: unknown;
}

export interface TestSession {
    id: string;
    user_id: number;
    test_id: number;
    start_time: string;
    end_time?: string;
    last_activity: string;
    time_remaining_seconds: number;
    status: 'in_progress' | 'completed' | 'expired';
    is_submitted: boolean;
    current_question_index: number;
    answers: Record<string, TestAnswer>;
    score?: number;
    correct_answers?: number;
}

export interface TestSessionCreate {
    user_id: number;
    test_id: number;
}

export interface TestSessionUpdate {
    current_question_index?: number;
    answers?: Record<string, TestAnswer>;
    time_remaining_seconds?: number;
    last_activity?: string;
    status?: string;
    is_submitted?: boolean;
}

export interface TestSessionWithTest {
    id: string;
    user_id: number;
    test_id: number;
    start_time: string;
    end_time?: string;
    last_activity: string;
    time_remaining_seconds: number;
    status: 'in_progress' | 'completed' | 'expired';
    is_submitted: boolean;
    current_question_index: number;
    answers: Record<string, TestAnswer>;
    score?: number;
    correct_answers?: number;
    test: Test;
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
    },

    // Test Session APIs
    createTestSession: async (sessionData: TestSessionCreate): Promise<TestSession> => {
        const response = await client.post('/tests/sessions', sessionData);
        return response.data;
    },

    getTestSession: async (sessionId: string): Promise<TestSessionWithTest> => {
        const response = await client.get(`/tests/sessions/${sessionId}`);
        return response.data;
    },

    getMyTestSessions: async (): Promise<TestSession[]> => {
        const response = await client.get('/tests/sessions/user/me');
        return response.data;
    },

    updateTestSession: async (sessionId: string, updateData: TestSessionUpdate): Promise<TestSession> => {
        const response = await client.put(`/tests/sessions/${sessionId}`, updateData);
        return response.data;
    },

    submitSessionAnswer: async (sessionId: string, questionId: string, answer: TestAnswer): Promise<TestSession> => {
        const response = await client.post(`/tests/sessions/${sessionId}/answers/${questionId}`, { answer });
        return response.data;
    },

    submitTestSession: async (sessionId: string, answers?: Record<string, TestAnswer>): Promise<TestResult> => {
        const response = await client.post(`/tests/sessions/${sessionId}/submit`, { answers });
        return response.data;
    },

    createTestSessionFromCourseEntryTest: async (courseId: number): Promise<TestSession> => {
        const response = await client.post(`/courses/${courseId}/entry-test/start`);
        return response.data;
    },

    getCourseEntryTest: async (courseId: number): Promise<Test> => {
        const response = await client.get(`/courses/${courseId}/entry-test`);
        return response.data;
    }
}; 