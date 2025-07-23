"use client";

import { discussionsApi } from "@/lib/api";
import { repliesApi, type Reply } from "@/lib/api/replies";
import { notFound } from "next/navigation";
import { Container, Title, Group, Badge, Text, Card } from "@mantine/core";
import { IconMessageCircle } from "@tabler/icons-react";
import ReactMarkdown from "react-markdown";
import ReplySection from "@/components/discussions/Reply";
import { useEffect, useState } from "react";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function DiscussionDetailPage({ params }: Props) {
  const { id } = await params;
  if (!id) return notFound();
  if (isNaN(Number(id))) return notFound();
  const idNumber = Number(id);
  const [discussion, setDiscussion] = useState<
    import("@/lib/api/discussions").Discussion | null
  >(null);
  const [replies, setReplies] = useState<Reply[]>([]);
  const [loading, setLoading] = useState(true);
  const [notFoundFlag, setNotFoundFlag] = useState(false);

  const fetchDiscussion = async () => {
    try {
      const data = await discussionsApi.getDiscussion(idNumber);
      setDiscussion(data);
    } catch {
      setNotFoundFlag(true);
    }
  };

  const fetchReplies = async () => {
    try {
      const data = await repliesApi.getRepliesByDiscussion(idNumber);
      setReplies(data.replies);
    } catch {
      setReplies([]);
    }
  };

  useEffect(() => {
    setLoading(true);
    Promise.all([fetchDiscussion(), fetchReplies()]).finally(() =>
      setLoading(false)
    );
    // eslint-disable-next-line
  }, [id]);

  if (notFoundFlag) return notFound();
  if (loading || !discussion) return null;

  return (
    <Container size="sm" py="xl">
      <Card
        withBorder
        className="bg-background/50 border-foreground/10 theme-transition p-6">
        <Group align="flex-start" gap="lg">
          <div className="flex flex-col items-center min-w-[64px]">
            <div className="mb-2">
              <div className="rounded-full bg-primary/20 w-16 h-16 flex items-center justify-center text-2xl font-bold text-primary">
                {discussion.author[0]}
              </div>
            </div>
            <Text fw={500} size="md" className="text-foreground">
              {discussion.author}
            </Text>
            <Text size="xs" c="dimmed">
              {new Date(discussion.createdAt).toLocaleDateString()}
            </Text>
          </div>
          <div className="flex-1">
            <Group justify="space-between" mb="xs">
              <Title order={3} className="text-gradient-theme font-semibold">
                {discussion.title}
              </Title>
              <Badge
                variant="light"
                className="bg-primary/20 text-primary border-primary/30">
                {discussion.category}
              </Badge>
            </Group>
            <Group gap="md" mt="sm" className="text-foreground/70">
              <Group gap="xs">
                <IconMessageCircle size={16} />
                <Text size="sm">{discussion.replies} replies</Text>
              </Group>
            </Group>
            <div className="mt-4 text-foreground/80 text-base prose max-w-none">
              <ReactMarkdown>{discussion.content}</ReactMarkdown>
            </div>
          </div>
        </Group>
        <ReplySection
          replies={replies}
          reloadReplies={fetchReplies}
          discussionId={idNumber}
        />
      </Card>
    </Container>
  );
}
