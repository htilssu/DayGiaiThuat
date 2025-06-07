"use client";

import { ActionIcon, Group, Title } from "@mantine/core";
import { IconMoonStars, IconSun } from "@tabler/icons-react";
import { useEffect, useState } from "react";

export function AdminHeader() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    // Get initial theme from localStorage or system preference
    const savedTheme = localStorage.getItem("theme") as "light" | "dark";
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute("data-theme", savedTheme);
    } else {
      const systemTheme = window.matchMedia("(prefers-color-scheme: dark)")
        .matches
        ? "dark"
        : "light";
      setTheme(systemTheme);
      document.documentElement.setAttribute("data-theme", systemTheme);
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
  };

  return (
    <header className="border-b border-primary/10 bg-primary/5">
      <div className="container mx-auto px-4 sm:px-6 py-4">
        <Group justify="space-between" align="center">
          <div className="flex items-center gap-x-3">
            <Title order={3} className="text-gradient-theme font-semibold">
              Admin Dashboard
            </Title>
          </div>

          <div className="flex items-center gap-x-4">
            <ActionIcon
              variant="light"
              size="lg"
              className="bg-primary/10 text-primary hover:bg-primary/20"
              onClick={toggleTheme}
              aria-label="Toggle theme">
              {theme === "dark" ? (
                <IconSun size={20} stroke={1.5} />
              ) : (
                <IconMoonStars size={20} stroke={1.5} />
              )}
            </ActionIcon>
          </div>
        </Group>
      </div>
    </header>
  );
}
