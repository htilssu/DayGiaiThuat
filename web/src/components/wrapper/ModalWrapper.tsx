'use client'

import { useAppSelector, useAppDispatch } from '@/lib/store';
import { removeModal, modalCallbacks } from '@/lib/store/modalStore';
import React from 'react'

export default function ModalWrapper({ children }: { children: React.ReactNode }) {
    const modals = useAppSelector((state) => state.modal.modals);
    const dispatch = useAppDispatch();

    if (typeof window === 'undefined') return children;
    if (modals.length === 0) {
        document.body.style.overflow = 'auto';
    } else {
        document.body.style.overflow = 'hidden';
    }

    return (
        <div>
            {children}

            {modals.length > 0 && modals.map((modal) => (
                <div key={modal.id} className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/50">
                    <div className="bg-background rounded-xl shadow-lg p-6 max-w-md w-full mx-4">
                        <h2 className="text-xl font-bold mb-2">{modal.title}</h2>
                        <div className="mb-6 text-foreground/80">
                            {typeof modal.description === 'string' ? modal.description : modal.description}
                        </div>
                        <div className="flex justify-end gap-3">
                            <button
                                onClick={() => {
                                    const callbacks = modalCallbacks.get(modal.id);
                                    if (callbacks) {
                                        callbacks.onCancel();
                                    }
                                    dispatch(removeModal(modal.id));
                                }}
                                className="px-4 py-2 rounded-lg border border-foreground/20 hover:bg-foreground/5"
                            >
                                {modal.cancelText || "Hủy"}
                            </button>
                            <button
                                onClick={() => {
                                    const callbacks = modalCallbacks.get(modal.id);
                                    if (callbacks) {
                                        callbacks.onConfirm();
                                    }
                                    dispatch(removeModal(modal.id));
                                }}
                                className="px-4 py-2 bg-primary text-white rounded-lg hover:opacity-90"
                            >
                                {modal.confirmText || "Xác nhận"}
                            </button>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}