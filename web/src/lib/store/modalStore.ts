import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { ReactNode } from "react";

export type Modal = {
    id: string;
    title: string;
    description: string | ReactNode;
    onConfirm: () => void;
    onCancel: () => void;
}

export const modalStore = createSlice({
    name: "modal",
    initialState: {
        modals: [] as Modal[],
    },
    reducers: {
        addModal: (state, action: PayloadAction<Modal>) => {
            state.modals.push(action.payload);
        },
        removeModal: (state, action: PayloadAction<string>) => {
            state.modals = state.modals.filter((modal) => modal.id !== action.payload);
        },
    },
});

export const { addModal, removeModal } = modalStore.actions;

export default modalStore.reducer;