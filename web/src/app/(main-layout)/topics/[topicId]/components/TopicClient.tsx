'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button, Loader, Alert } from '@mantine/core';
import { IconAlertCircle, IconExternalLink } from '@tabler/icons-react';
import { testApi, Test } from '@/lib/api';

interface TopicClientProps {
    topicId: string;
    topic: {
        title: string;
        description: string;
        color: string;
        icon: string;
    };
    lessons: {
        id: string;
        title: string;
        description: string;
    }[];
}

const TopicClient: React.FC<TopicClientProps> = ({ topicId, topic, lessons }) => {
    const router = useRouter();
    const [test, setTest] = useState<Test | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    return <></>
};

export default TopicClient; 