"use client";

import { useEffect, useState, useMemo } from "react";
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
import { discussionsApi, type Discussion } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useAppSelector } from "@/lib/store";
import Link from "next/link";

export default function DiscussionsPage() {
  const router = useRouter();
  const user = useAppSelector((state) => state.user.user);
  const [isLoading, setIsLoading] = useState(true);
  const [discussions, setDiscussions] = useState<Discussion[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  type SortByType =
    | "newest"
    | "oldest"
    | "author-asc"
    | "author-desc"
    | "replies-asc"
    | "replies-desc";
  const [sortBy, setSortBy] = useState<SortByType>("newest");
  const [category, setCategory] = useState<string>("");
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ title: "", content: "", category: "" });
  const [modalLoading, setModalLoading] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  const fetchDiscussions = async () => {
    try {
      setIsLoading(true);
      const backendSorts: SortByType[] = ["newest", "oldest", "replies-desc", "replies-asc", "author-asc", "author-desc"];
      const response = await discussionsApi.getDiscussions({
        search: searchQuery,
        sortBy: backendSorts.includes(sortBy)
          ? (sortBy as import("@/lib/api/discussions").GetDiscussionsParams["sortBy"])
          : "newest",
        category: category || undefined,
        page,
        limit: 10,
      });
      let sorted = response.discussions;
      // Fallback client-side sort for author/replies if backend doesn't support
      if (sortBy === "author-asc") {
        sorted = [...sorted].sort((a, b) => a.author.localeCompare(b.author));
      } else if (sortBy === "author-desc") {
        sorted = [...sorted].sort((a, b) => b.author.localeCompare(a.author));
      } else if (sortBy === "replies-asc") {
        sorted = [...sorted].sort((a, b) => a.replies - b.replies);
      } else if (sortBy === "replies-desc") {
        sorted = [...sorted].sort((a, b) => b.replies - a.replies);
      }
      setDiscussions(sorted);
      setTotalPages(response.totalPages);
    } catch (error) {
      console.error("Failed to fetch discussions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDiscussions();
  }, [page, sortBy, category]);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (page !== 1) setPage(1);
      else fetchDiscussions();
    }, 500);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1);
  }, [sortBy, category]);

  // Get unique categories from discussions for filter options
  const categoryOptions = useMemo(() => {
    const cats = new Set<string>();
    discussions.forEach((d) => {
      if (d.category) cats.add(d.category);
    });
    return Array.from(cats).map((cat) => ({ value: cat, label: cat }));
  }, [discussions]);

  if (!user) {
    return (
      <Container size="lg" py="xl">
        <div className="flex flex-col items-center justify-center min-h-[40vh]">
          <Title order={3} className="text-gradient-theme font-semibold mb-2">
            Please log in to view discussions
          </Title>
          <Button
            onClick={() => router.push("/auth/login")}
            variant="gradient"
            gradient={{
              from: "rgb(var(--color-primary))",
              to: "rgb(var(--color-secondary))",
            }}>
            Go to Login
          </Button>
        </div>
      </Container>
    );
  }

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
            onClick={() => setShowModal(true)}>
            New Discussion
          </Button>
        </div>

        {/* Modal for creating new discussion */}
        {showModal && (
          <div>
            <div className="h-full w-full absolute top-0 left-0 z-98 bg-black opacity-40"></div>
            <div className="fixed inset-0 z-99 flex items-center h-full justify-center bg-transparent">
              <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6 relative opacity-100">
                <h2 className="text-xl font-semibold mb-4">
                  Create New Discussion
                </h2>
                {modalError && (
                  <div className="mb-2 text-red-600 text-sm border border-red-200 bg-red-50 rounded px-2 py-1">
                    {modalError}
                  </div>
                )}
                <form
                  className="space-y-4"
                  onSubmit={async (e) => {
                    e.preventDefault();
                    setModalLoading(true);
                    setModalError(null);
                    try {
                      await discussionsApi.createDiscussion(form);
                      setShowModal(false);
                      setForm({ title: "", content: "", category: "" });
                      fetchDiscussions();
                    } catch {
                      setModalError(
                        "Failed to create discussion. Please try again."
                      );
                    } finally {
                      setModalLoading(false);
                    }
                  }}>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Title
                    </label>
                    <input
                      type="text"
                      className="w-full border rounded px-3 py-2"
                      value={form.title}
                      onChange={(e) =>
                        setForm((f) => ({ ...f, title: e.target.value }))
                      }
                      required
                      disabled={modalLoading}
                      placeholder="Enter discussion title"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Content
                    </label>
                    <textarea
                      className="w-full border rounded px-3 py-2"
                      rows={4}
                      value={form.content}
                      onChange={(e) =>
                        setForm((f) => ({ ...f, content: e.target.value }))
                      }
                      required
                      disabled={modalLoading}
                      placeholder="Enter discussion content"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Category
                    </label>
                    <input
                      type="text"
                      className="w-full border rounded px-3 py-2"
                      value={form.category}
                      onChange={(e) =>
                        setForm((f) => ({ ...f, category: e.target.value }))
                      }
                      required
                      disabled={modalLoading}
                      placeholder="Enter category"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      type="button"
                      className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
                      onClick={() => {
                        setShowModal(false);
                        setModalError(null);
                      }}
                      disabled={modalLoading}>
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 rounded bg-primary text-white hover:bg-primary/90"
                      disabled={modalLoading}>
                      {modalLoading ? "Creating..." : "Create"}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

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
              value={category}
              onChange={(value) => setCategory(value || "")}
              data={[
                { value: "", label: "All Categories" },
                ...categoryOptions,
              ]}
              placeholder="Filter by category"
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
              onChange={(value) => setSortBy((value || "newest") as SortByType)}
              data={[
                { value: "newest", label: "Newest First" },
                { value: "oldest", label: "Oldest First" },
                { value: "replies-desc", label: "Most Replies" },
                { value: "replies-asc", label: "Fewest Replies" },
                { value: "author-asc", label: "Author A-Z" },
                { value: "author-desc", label: "Author Z-A" },
              ]}
              placeholder="Sort by"
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
                <Link
                  key={discussion.id}
                  href={`/discussions/${discussion.id}`}>
                  <Card
                    withBorder
                    className="bg-background/50 border-foreground/10 hover:border-primary/30 transition-all hover:shadow-md cursor-pointer theme-transition">
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
                </Link>
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
