'use client'
import React from "react";
import QueryWrapper from "./QueryWrapper";

export default function ClientWrapper({ children }: { children: React.ReactNode }) {
    return <>
        <QueryWrapper>
            {children}
        </QueryWrapper>
    </>;
}