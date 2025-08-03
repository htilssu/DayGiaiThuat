"use client";
import { useState } from "react";
import { Card, Group, Textarea, Button, Text, Avatar } from "@mantine/core";
import { repliesApi, type Reply } from "@/lib/api/replies";

interface ReplySectionProps {
  replies: Reply[];
  reloadReplies: () => Promise<void>;
  discussionId: number;
  isLoading?: boolean;
}

export default function ReplySection({
  replies,
  reloadReplies,
  discussionId,
  isLoading = false,
}: ReplySectionProps) {
  const [input, setInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setIsSubmitting(true);
    try {
      await repliesApi.createReply({ discussionId, content: input });
      setInput("");
      await reloadReplies();
    } finally {
      setIsSubmitting(false);
    }
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
