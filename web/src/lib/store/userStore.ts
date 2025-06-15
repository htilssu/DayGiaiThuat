import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { UserData } from "../api";


type UserState = {
    isLoading: boolean;
    user: UserData | null;
    isInitial: boolean
}

export const userSlice = createSlice({
    initialState: {
        isLoading: false,
        user: null,
        isInitial: true
    } as UserState,
    name: "user",
    reducers: {
        setUser: (state, action: PayloadAction<UserData>) => {
            state = { ...state, isLoading: false, isInitial: false }
        },
        removeUser: (state) => {
            state = { ...state, user: null }
        },
        loadingUser: (state) => {
            state = { ...state, isInitial: false, isLoading: true }
        }
    }
})

export const { loadingUser, removeUser, setUser } = userSlice.actions

export default userSlice.reducer