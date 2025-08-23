import { get, post, patch } from './client';

export interface TestQuestion {
    id: string;
    content: string;
    type: 'single_choice' | 'essay';
    difficulty?: string;
    answer?: string;
    options?: string[];
}

export interface Test {
    id: number;
    courseId?: number;
    topicId?: number;
    questions: TestQuestion[];
    durationMinutes: number;
    passingScore?: number;
    maxAttempts?: number;
    isPublic?: boolean;
    createdAt: string;
    updatedAt: string;
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
    completedAt?: string;
    feedback?: Record<string, {
        isCorrect: boolean;
        feedback?: string;
    }>;
}

export interface TestAnswer {
    selectedOptionId?: string;
    code?: string;
    [key: string]: unknown;
}

export interface TestSession {
    id: string;
    userId: number;
    testId: number;
    startTime?: string | null;
    endTime?: string | null;
    timeRemainingSeconds: number;
    status: 'pending' | 'in_progress' | 'completed' | 'expired';
    isSubmitted: boolean;
    currentQuestionIndex: number;
    score?: number | null;
    correctAnswers?: number | null;
    answers: Record<string, {
        selectedOptionId?: string;
        code?: string;
        feedback?: {
            isCorrect: boolean;
            feedback?: string;
        };
    }>;
    createdAt: string;
    updatedAt: string;
}

export interface TestSessionWithTest extends TestSession {
    test: Test;
}

export interface TestHistorySummary {
    sessionId: string;
    testId: number;
    topicId?: number;
    courseId?: number;
    testName: string;
    startTime?: string | null;
    endTime?: string | null;
    durationMinutes: number;
    score?: number;
    correctAnswers?: number;
    totalQuestions: number;
    status: string;
}

export interface CreateTestSessionRequest {
    testId: number;
}

export interface UpdateTestSessionRequest {
    currentQuestionIndex?: number;
    timeRemainingSeconds?: number;
}

export const testApi = {
    // Get all available tests
    getTests: async (): Promise<Test[]> => {
        return await get('/tests');
    },

    // Get available tests for a topic
    getTestsByTopic: async (topicId: number): Promise<Test[]> => {
        return await get(`/tests/topic/${topicId}`);
    },

    // Get available tests for a course (entry test)
    getTestsByCourse: async (courseId: number): Promise<Test[]> => {
        return await get(`/tests/course/${courseId}`);
    },

    // Get test by ID
    getTestById: async (testId: number): Promise<Test> => {
        return await get(`/tests/${testId}`);
    },

    // Create a new test session
    createTestSession: async (request: CreateTestSessionRequest): Promise<TestSession> => {
        return await post('/tests/sessions', request);
    },

    // Start test session (mark as actively started)
    startTestSession: async (sessionId: string): Promise<TestSession> => {
        return await post(`/tests/sessions/${sessionId}/start`, {});
    },

    // Get test session with test details
    getTestSession: async (sessionId: string): Promise<TestSessionWithTest> => {
        return await get(`/tests/sessions/${sessionId}`);
    },

    // Update test session (progress, time)
    updateTestSession: async (sessionId: string, updates: UpdateTestSessionRequest): Promise<TestSession> => {
        return await patch(`/tests/sessions/${sessionId}`, updates);
    },

    // Submit entire test session
    submitTestSession: async (
        sessionId: string,
        answers: Record<string, { selectedOptionId?: string; code?: string }>
    ): Promise<TestResult> => {
        return await post(`/tests/sessions/${sessionId}/submit`, { answers });
    },

    // Get user's test history (summary only)
    getUserTestHistory: async (): Promise<TestHistorySummary[]> => {
        return await get('/tests/test-history');
    },

    // Get test results by session ID
    getTestResult: async (sessionId: string): Promise<TestResult> => {
        return await get(`/tests/sessions/${sessionId}/result`);
    },

    // Resume test session (if exists)
    resumeTestSession: async (testId: number): Promise<TestSessionWithTest | null> => {
        try {
            return await get(`/tests/${testId}/resume`);
        } catch (error: any) {
            if (error.response?.status === 404) {
                return null;
            }
            throw error;
        }
    },

    // Check if user can take test (based on prerequisites, attempts, etc.)
    canTakeTest: async (testId: number): Promise<{ canTake: boolean; reason?: string }> => {
        return await get(`/tests/${testId}/can-take`);
    },

    // WebSocket connection for real-time test session updates
    connectToTestSession: (sessionId: string): WebSocket => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') ||
            window.location.host.replace(':3000', ':8000');
        const wsUrl = `${protocol}//${host}/tests/ws/test-sessions/${sessionId}`;

        return new WebSocket(wsUrl);
    },

    // Sync test session state (fallback when WebSocket disconnects)
    syncTestSession: async (sessionId: string): Promise<TestSessionWithTest> => {
        return await get(`/tests/sessions/${sessionId}/sync`);
    },

    // Check session access
    checkSessionAccess: async (sessionId: string): Promise<{
        can_access: boolean;
        reason?: string;
        message: string;
        session?: TestSession;
    }> => {
        return await get(`/tests/sessions/${sessionId}/access-check`);
    }
}; 