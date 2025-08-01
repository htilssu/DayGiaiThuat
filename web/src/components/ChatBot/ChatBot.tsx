"use client";

import { useState } from "react";
import { IconMessage, IconX } from "@tabler/icons-react";
import { Paper, ActionIcon, Transition } from "@mantine/core";
import ChatInterface from "./ChatInterface";
import { useAppSelector } from "@/lib/store";

export default function ChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const userState = useAppSelector((state) => state.user);

  return (
    <div className={`fixed bottom-16 right-4 z-50 ${userState.user === null ? "hidden" : "block"}`}>
      <Transition
        mounted={isOpen}
        transition="slide-up"
        duration={400}
        timingFunction="ease">
        {(styles) => (
          <Paper
            shadow="lg"
            className="-mb-22 md:w-[25rem] w-[20rem] h-[520px] rounded-xl overflow-hidden border border-[rgb(var(--color-primary))] bg-[rgb(var(--color-background))]"
            style={styles}>
            <div className="absolute top-2 right-2 z-10">
              <ActionIcon
                onClick={() => setIsOpen(false)}
                variant="light"
                color="white"
                radius="xl">
                <IconX size={23} />
              </ActionIcon>
            </div>
            <ChatInterface />
          </Paper>
        )}
      </Transition>

      <div className="w-full flex justify-end">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`
          group flex items-center gap-2 px-4 py-2 rounded-full
          bg-gradient-to-r from-[rgb(var(--color-primary))] to-[rgb(var(--color-secondary))]
          text-white shadow-lg hover:shadow-xl
          transition-all duration-300 ease-in-out
          ${isOpen ? "opacity-0" : "opacity-100"}
        `}>
          <IconMessage
            size={20}
            className="group-hover:rotate-12 transition-transform duration-300"
          />
          <span className="text-sm font-medium">Chat</span>
        </button>
      </div>
    </div >
  );
}
