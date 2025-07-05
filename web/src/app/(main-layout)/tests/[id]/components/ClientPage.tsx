'use client';

import React, { useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { TestPageNew } from '@/components/test';
import { useAppSelector } from '@/lib/store';

const ClientPage: React.FC = () => {
    const params = useParams();
    const router = useRouter();
    const sessionId = params.id as string;
    const userState = useAppSelector((state) => state.user);

    // Redirect if not authenticated
    useEffect(() => {
        if (!userState.isLoading && !userState.isInitial && !userState.user) {
            router.push('/auth/login');
        }
    }, [userState, router]);

    // Show loading during auth check
    if (userState.isLoading || userState.isInitial) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Đang kiểm tra quyền truy cập...</p>
                </div>
            </div>
        );
    }

    // If not authenticated, will be redirected by useEffect
    if (!userState.user) {
        return null;
    }

    // Render the new test page component
    return <TestPageNew sessionId={sessionId} />;
};

export default ClientPage; 