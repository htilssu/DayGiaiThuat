"use client";

import { useEffect, useState } from "react";
import {
  Container,
  Title,
  TextInput,
  Button,
  Group,
  Card,
  Text,
  Stack,
  Select,
  Badge,
  Loader,
  Pagination,
} from "@mantine/core";
import {
  IconSearch,
  IconPlus,
  IconMessageCircle,
  IconCalendar,
} from "@tabler/icons-react";
import { discussionsApi, type Discussion } from "@/lib/api/discussions";
import { useRouter } from "next/navigation";

export default function DiscussionsPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [discussions, setDiscussions] = useState<Discussion[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortBy, setSortBy] = useState<string>("newest");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchDiscussions = async () => {
    try {
      setIsLoading(true);
      const response = await discussionsApi.getDiscussions({
        search: searchQuery,
        sortBy: sortBy as "newest" | "oldest" | "most-replies",
        page,
        limit: 10,
      });
      setDiscussions(response.discussions);
      setTotalPages(response.totalPages);
    } catch (error) {
      console.error("Failed to fetch discussions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiscussions();
  }, [page, sortBy]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (page !== 1) setPage(1);
      else fetchDiscussions();
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  return (
    <Container size="lg" py="xl">
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <Title order={2} className="text-gradient-theme font-semibold">
            Discussions
          </Title>
          <Button
            leftSection={<IconPlus size={20} />}
            variant="gradient"
            gradient={{
              from: "rgb(var(--color-primary))",
              to: "rgb(var(--color-secondary))",
            }}
            className="transition-all hover:shadow-md"
            onClick={() => router.push("/discussions/new")}>
            New Discussion
          </Button>
        </div>

        <div className="bg-background rounded-xl shadow-sm p-6 border border-foreground/10 theme-transition">
          <Group mb="lg" grow>
            <TextInput
              placeholder="Search discussions..."
              leftSection={<IconSearch size={16} className="text-primary/70" />}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.currentTarget.value)}
              className="flex-1"
              styles={{
                input: {
                  "&:focus": {
                    borderColor: "rgb(var(--color-primary))",
                  },
                },
              }}
            />
            <Select
              value={sortBy}
              onChange={(value) => setSortBy(value || "newest")}
              data={[
                { value: "newest", label: "Newest First" },
                { value: "oldest", label: "Oldest First" },
                { value: "most-replies", label: "Most Replies" },
              ]}
              styles={{
                input: {
                  "&:focus": {
                    borderColor: "rgb(var(--color-primary))",
                  },
                },
              }}
            />
          </Group>

          {isLoading ? (
            <Group justify="center" py="xl">
              <Loader color="rgb(var(--color-primary))" />
            </Group>
          ) : (
            <Stack gap="md">
              {discussions.map((discussion) => (
                <Card
                  key={discussion.id}
                  withBorder
                  className="bg-background/50 border-foreground/10 hover:border-primary/30 transition-all hover:shadow-md cursor-pointer theme-transition"
                  onClick={() => router.push(`/discussions/${discussion.id}`)}>
                  <Group justify="space-between" mb="xs">
                    <Text size="lg" fw={500} className="text-foreground">
                      {discussion.title}
                    </Text>
                    <Badge
                      variant="light"
                      className="bg-primary/20 text-primary border-primary/30">
                      {discussion.category}
                    </Badge>
                  </Group>

                  <Group gap="xl" mt="md" className="text-foreground/70">
                    <Group gap="xs">
                      <Text size="sm">By {discussion.author}</Text>
                    </Group>
                    <Group gap="xs">
                      <IconCalendar size={16} />
                      <Text size="sm">
                        {new Date(discussion.createdAt).toLocaleDateString()}
                      </Text>
                    </Group>
                    <Group gap="xs">
                      <IconMessageCircle size={16} />
                      <Text size="sm">{discussion.replies} replies</Text>
                    </Group>
                  </Group>
                </Card>
              ))}
            </Stack>
          )}

          {totalPages > 1 && (
            <Group justify="center" mt="xl">
              <Pagination
                value={page}
                onChange={setPage}
                total={totalPages}
                color="blue"
                radius="md"
                styles={{
                  control: {
                    "&[data-active]": {
                      backgroundImage:
                        "linear-gradient(to right, rgb(var(--color-primary)), rgb(var(--color-secondary)))",
                    },
                  },
                }}
              />
            </Group>
          )}
        </div>
      </div>
    </Container>
  );
}
