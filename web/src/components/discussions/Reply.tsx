"use client";
import { useState } from "react";
import { Card, Group, Textarea, Button, Text, Avatar } from "@mantine/core";

interface Reply {
  id: number;
  author: string;
  content: string;
  createdAt: string;
}

export default function ReplySection() {
  const [replies, setReplies] = useState<Reply[]>([
    {
      id: 1,
      author: "Jane Doe",
      content:
        "Great question! I think binary search is all about keeping track of your left and right pointers.",
      createdAt: new Date(Date.now() - 3600 * 1000 * 2).toISOString(),
    },
    {
      id: 2,
      author: "John Smith",
      content: "Check out the lesson linked above, it helped me a lot!",
      createdAt: new Date(Date.now() - 3600 * 1000 * 1).toISOString(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setIsSubmitting(true);
    setTimeout(() => {
      setReplies([
        ...replies,
        {
          id: replies.length + 1,
          author: "You",
          content: input,
          createdAt: new Date().toISOString(),
        },
      ]);
      setInput("");
      setIsSubmitting(false);
    }, 500);
  };

  return (
    <div className="mt-8">
      <Text fw={500} size="lg" mb="md">
        Replies
      </Text>
      <form onSubmit={handleSubmit} className="mb-6">
        <Textarea
          placeholder="Write your reply..."
          value={input}
          onChange={(e) => setInput(e.currentTarget.value)}
          minRows={3}
          autosize
          required
        />
        <Group justify="end" mt="xs">
          <Button type="submit" loading={isSubmitting} disabled={!input.trim()}>
            Reply
          </Button>
        </Group>
      </form>
      <div className="space-y-4">
        {replies.map((reply) => (
          <Card
            key={reply.id}
            withBorder
            className="bg-background/40 border-foreground/10">
            <Group align="flex-start" gap="md">
              <Avatar radius="xl" size="md">
                {reply.author[0]}
              </Avatar>
              <div>
                <Text fw={500} size="sm">
                  {reply.author}
                </Text>
                <Text size="xs" c="dimmed">
                  {new Date(reply.createdAt).toLocaleString()}
                </Text>
                {/* <Text mt={4}>{reply.content}</Text> */}
              </div>
            </Group>
            <div className="mt-4 text-foreground/80 text-base prose max-w-none">
              {reply.content}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
