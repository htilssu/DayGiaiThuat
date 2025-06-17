'use client'

import { useAppSelector } from '@/lib/store';
import React from 'react'

export default function ModalWrapper({ children }: { children: React.ReactNode }) {
    const modals = useAppSelector((state) => state.modal.modals);
    if (typeof window === 'undefined') return children;
    if (modals.length === 0) {
        document.body.style.overflow = 'auto';
    } else {
        document.body.style.overflow = 'hidden';
    }

    return (
        <div>
            {children}
        </div>
    )
}