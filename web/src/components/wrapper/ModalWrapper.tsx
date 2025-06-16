import { useAppSelector } from '@/lib/store';
import React from 'react'

export default function ModalWrapper({ children }: { children: React.ReactNode }) {
    const modals = useAppSelector((state) => state.modal.modals);

    if (modals.length === 0) return children;

    return (
        <div></div>
    )
}