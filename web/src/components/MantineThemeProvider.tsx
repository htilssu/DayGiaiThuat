"use client";

import React from "react";
import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';

/**
 * Component MantineThemeProvider để tích hợp theme của Mantine với theme chung của ứng dụng
 * @param {Object} props - Thuộc tính của component
 * @param {React.ReactNode} props.children - Các component con
 */
export function MantineThemeProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <MantineProvider
      theme={{
        primaryColor: "blue",
        defaultRadius: "md",
        fontFamily: "var(--font-geist-sans), -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        fontFamilyMonospace: "var(--font-geist-mono), 'Fira Code', monospace",
        colors: {
          primary: [
            '#e6f7f2',
            '#ccefde',
            '#99dfbd',
            '#66cf9c',
            '#33bf7b',
            '#00af5a',
            '#008c48',
            '#006936',
            '#004624',
            '#002312'
          ],
        },
        spacing: {
          xs: '0.5rem',
          sm: '0.75rem',
          md: '1rem',
          lg: '1.5rem',
          xl: '2rem',
        },
        shadows: {
          xs: '0 1px 3px rgba(0, 0, 0, 0.1)',
          sm: '0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24)',
          md: '0 3px 6px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12)',
          lg: '0 10px 20px rgba(0, 0, 0, 0.15), 0 3px 6px rgba(0, 0, 0, 0.10)',
          xl: '0 15px 25px rgba(0, 0, 0, 0.15), 0 5px 10px rgba(0, 0, 0, 0.05)',
        },
        headings: {
          fontFamily: "var(--font-geist-sans), -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
          fontWeight: '600',
        },
      }}
    >
      <Notifications position="top-right" zIndex={2077} />
      {children}
    </MantineProvider>
  );
}
