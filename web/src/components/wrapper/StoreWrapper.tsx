'use client'
import { store } from '@/lib/store'
import React from 'react'
import { Provider } from 'react-redux'
import { AuthProvider } from '@/contexts/AuthContext'

export default function StoreWrapper({ children }: { children: React.ReactNode }) {
    return (
        <Provider store={store}>
            <AuthProvider>
                {children}
            </AuthProvider>
        </Provider>
    )
}
