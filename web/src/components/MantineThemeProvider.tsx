"use client";

import React from "react";
import { MantineProvider, createTheme } from "@mantine/core";
import { useTheme } from "@/contexts/ThemeContext";

/**
 * Theme Mantine tùy chỉnh
 */
const mantineTheme = createTheme({
  primaryColor: "blue",
  defaultRadius: "md",
  fontFamily: "var(--font-geist-sans)",
  fontFamilyMonospace: "var(--font-geist-mono)",
});

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
  const { theme } = useTheme();

  return (
    <MantineProvider
      theme={mantineTheme}
      forceColorScheme={theme === "dark" ? "dark" : "light"}
    >
      {children}
    </MantineProvider>
  );
}
