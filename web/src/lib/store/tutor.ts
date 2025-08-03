import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { UserData } from "../api";

type TutorState = {
    sessionId: string | null;
    type: "lesson" | "quiz";
    contextId: string | null;
}

export const tutorSlice = createSlice({
    initialState: {
        sessionId: null,
        type: "lesson",
        contextId: null
    } as TutorState,
    name: "tutor",
    reducers: {
        setSessionId: (state, action: PayloadAction<string | null>) => {
            state.sessionId = action.payload;
        },
        setType: (state, action: PayloadAction<"lesson" | "quiz">) => {
            state.type = action.payload;
        },
        setContextId: (state, action: PayloadAction<string | null>) => {
            state.contextId = action.payload;
        },
        reset: (state) => {
            state.sessionId = null;
            state.type = "lesson";
            state.contextId = null;
        },
        setState: (state, action: PayloadAction<TutorState>) => {
            if (action.payload.sessionId) {
                state.sessionId = action.payload.sessionId;
            }
            state.type = action.payload.type;
            state.contextId = action.payload.contextId;
        }
    }
});

export const { setSessionId, setType, setContextId, reset, setState } = tutorSlice.actions

export default tutorSlice.reducer