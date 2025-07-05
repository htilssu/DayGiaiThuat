import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { ReactNode } from "react";

// Lưu trữ các callback trong một Map bên ngoài Redux store
export const modalCallbacks = new Map<string, { onConfirm: () => void; onCancel: () => void }>();

export type Modal = {
    id: string;
    title: string;
    description: string | ReactNode;
    confirmText?: string;
    cancelText?: string;
}

export type ModalWithCallbacks = Modal & {
    onConfirm: () => void;
    onCancel: () => void;
}

export const modalStore = createSlice({
    name: "modal",
    initialState: {
        modals: [] as Modal[],
    },
    reducers: {
        addModal: (state, action: PayloadAction<ModalWithCallbacks>) => {
            const { onConfirm, onCancel, ...modalData } = action.payload;
            // Lưu callbacks vào Map
            modalCallbacks.set(modalData.id, { onConfirm, onCancel });
            // Chỉ lưu dữ liệu có thể serialize vào store
            state.modals.push(modalData);
        },
        removeModal: (state, action: PayloadAction<string>) => {
            // Xóa callbacks khỏi Map
            modalCallbacks.delete(action.payload);
            state.modals = state.modals.filter((modal) => modal.id !== action.payload);
        },
    },
});

export const { addModal, removeModal } = modalStore.actions;

export default modalStore.reducer;