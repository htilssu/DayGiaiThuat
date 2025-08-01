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
            state.user = action.payload;
            state.isLoading = false;
            state.isInitial = false;
        },
        removeUser: (state) => {
            state.user = null;
        },
        loadingUser: (state) => {
            state.isInitial = false;
            state.isLoading = true;
        },
        reloadUser: (state) => {
            state.isInitial = true;
        }
    }
})

export const { loadingUser, removeUser, setUser, reloadUser } = userSlice.actions

export default userSlice.reducer