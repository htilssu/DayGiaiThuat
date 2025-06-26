'use client';

import React from 'react';
import { TestPage } from '@/components/test';

interface ClientPageProps {
    sessionId: string;
}

const ClientPage: React.FC<ClientPageProps> = ({ sessionId }) => {
    return <TestPage sessionId={sessionId} />;
};

export default ClientPage; 