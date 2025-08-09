"use client";

import { useState } from "react";
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
  Modal,
  Textarea,
  LoadingOverlay,
} from "@mantine/core";
import {
  IconSearch,
  IconPlus,
  IconMessageCircle,
  IconCalendar,
  IconX,
} from "@tabler/icons-react";
import { useDiscussions } from "@/hooks/useDiscussions";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { discussionsApi } from "@/lib/api/discussions";
import { notifications } from "@mantine/notifications";
import { useAppSelector } from "@/lib/store";

export default function DiscussionsClient() {
  const router = useRouter();
  const user = useAppSelector((state) => state.user.user);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState<string>("newest");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    content: "",
    category: "",
  });

  // Use React Query to fetch discussions
  const {
    data: discussionsData,
    isLoading: loading,
    error,
    refetch,
  } = useDiscussions({
    search: searchTerm || undefined,
    category: categoryFilter !== "all" ? categoryFilter : undefined,
    sortBy: sortBy as "newest" | "oldest" | "most-replies",
    page: currentPage,
    limit: itemsPerPage,
  });

  const discussions = discussionsData?.discussions || [];
  const totalPages = discussionsData?.totalPages || 1;

  const handleCreateNew = () => {
    if (!user) {
      notifications.show({
        title: "Authentication Required",
        message: "Please log in to create a discussion",
        color: "yellow",
      });
      return;
    }
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setFormData({ title: "", content: "", category: "" });
  };

  const handleSubmit = async () => {
    if (
      !formData.title.trim() ||
      !formData.content.trim() ||
      !formData.category.trim()
    ) {
      notifications.show({
        title: "Validation Error",
        message: "Please fill in all fields",
        color: "red",
      });
      return;
    }

    setIsCreating(true);
    try {
      console.log("Creating discussion with data:", formData);
      const result = await discussionsApi.createDiscussion({
        title: formData.title.trim(),
        content: formData.content.trim(),
        category: formData.category.trim(),
      });
      console.log("Discussion created successfully:", result);

      notifications.show({
        title: "Success",
        message: "Discussion created successfully!",
        color: "green",
      });

      handleCloseModal();
      refetch(); // Refresh the discussions list
    } catch (error) {
      console.error("Error creating discussion:", error);

      // More detailed error message
      let errorMessage = "Failed to create discussion. Please try again.";
      if (error && typeof error === "object" && "message" in error) {
        errorMessage = error.message as string;
      } else if (error && typeof error === "object" && "data" in error) {
        const errorData = (error as { data?: { detail?: string } }).data;
        if (errorData && errorData.detail) {
          errorMessage = errorData.detail;
        }
      }

      notifications.show({
        title: "Error",
        message: errorMessage,
        color: "red",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1); // Reset to first page when searching
    refetch();
  };

  const handleFilterChange = (value: string | null) => {
    setCategoryFilter(value || "all");
    setCurrentPage(1); // Reset to first page when filtering
  };

  const handleSortChange = (value: string | null) => {
    setSortBy(value || "newest");
    setCurrentPage(1); // Reset to first page when sorting
  };

  // Get unique categories from current discussions for filter options
  const categories = Array.from(new Set(discussions.map((d) => d.category)));

  //   if (error) {
  //     return (
  //       <Container size="lg" py="xl">
  //         <Card
  //           withBorder
  //           className="bg-background/50 border-foreground/10 theme-transition p-6">
  //           <Text className="text-foreground">
  //             Error loading discussions. Please try again.
  //           </Text>
  //           <Button
  //             onClick={() => refetch()}
  //             mt="md"
  //             className="bg-primary hover:bg-primary/90">
  //             Retry
  //           </Button>
  //         </Card>
  //       </Container>
  //     );
  //   }

  return (
    <Container size="lg" py="xl">
      <Group justify="space-between" mb="xl">
        <Title order={1} className="text-foreground">
          Discussions
        </Title>
        <Button
          leftSection={<IconPlus size={16} />}
          className="bg-primary hover:bg-primary/90"
          onClick={handleCreateNew}>
          {user ? "New Discussion" : "Login to Create Discussion"}
        </Button>
      </Group>

      {/* Search and Filter Controls */}
      <Card withBorder mb="xl" className="border-border">
        <Stack gap="md">
          <Group>
            <TextInput
              placeholder="Search discussions..."
              leftSection={<IconSearch size={16} />}
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.currentTarget.value)}
              className="flex-1"
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSearch();
                }
              }}
            />
            <Button
              onClick={handleSearch}
              className="bg-primary hover:bg-primary/90">
              Search
            </Button>
          </Group>
          <Group>
            <Select
              placeholder="Sort by"
              value={sortBy}
              onChange={handleSortChange}
              data={[
                { value: "newest", label: "Newest" },
                { value: "oldest", label: "Oldest" },
                { value: "most-replies", label: "Most Replies" },
              ]}
              className="min-w-[150px]"
            />
            <Select
              placeholder="Category"
              value={categoryFilter}
              onChange={handleFilterChange}
              data={[
                { value: "all", label: "All Categories" },
                ...categories.map((cat) => ({ value: cat, label: cat })),
              ]}
              className="min-w-[150px]"
            />
          </Group>
        </Stack>
      </Card>

      {/* Discussions List */}
      {loading ? (
        <Group justify="center" py="xl">
          <Loader />
        </Group>
      ) : (
        <div>
          {discussions.length === 0 ? (
            <Card withBorder className="border-border">
              <Text ta="center" py="xl" className="text-muted-foreground">
                No discussions found.
              </Text>
            </Card>
          ) : (
            <Stack gap="md">
              {discussions.map((discussion) => (
                <Link
                  key={discussion.id}
                  href={`/discussions/${discussion.id}`}
                  className="no-underline">
                  <Card
                    withBorder
                    className="border-border hover:border-primary/50 transition-colors cursor-pointer">
                    <Group justify="space-between" align="flex-start">
                      <Text
                        fw={600}
                        size="lg"
                        className="text-foreground hover:text-primary transition-colors">
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
                value={currentPage}
                onChange={setCurrentPage}
                total={totalPages}
                className="text-foreground"
              />
            </Group>
          )}
        </div>
      )}

      {/* Create Discussion Modal */}
      <Modal
        opened={isModalOpen}
        onClose={handleCloseModal}
        title="Create New Discussion"
        size="lg"
        closeOnClickOutside={!isCreating}
        closeOnEscape={!isCreating}>
        <div className="relative">
          <LoadingOverlay visible={isCreating} />
          <Stack gap="md">
            <TextInput
              label="Title"
              placeholder="Enter discussion title"
              value={formData.title}
              onChange={(event) =>
                setFormData({ ...formData, title: event.currentTarget.value })
              }
              required
            />

            <Textarea
              label="Content"
              placeholder="Enter your discussion content"
              value={formData.content}
              onChange={(event) =>
                setFormData({ ...formData, content: event.currentTarget.value })
              }
              minRows={4}
              required
            />

            <Select
              label="Category"
              placeholder="Select a category"
              value={formData.category}
              onChange={(value) =>
                setFormData({ ...formData, category: value || "" })
              }
              data={[
                { value: "General", label: "General" },
                { value: "Technical", label: "Technical" },
                { value: "Help", label: "Help" },
                { value: "Feedback", label: "Feedback" },
                { value: "Announcement", label: "Announcement" },
                ...categories
                  .filter(
                    (cat) =>
                      ![
                        "General",
                        "Technical",
                        "Help",
                        "Feedback",
                        "Announcement",
                      ].includes(cat)
                  )
                  .map((cat) => ({ value: cat, label: cat })),
              ]}
              required
            />

            <Group justify="flex-end" mt="md">
              <Button
                variant="outline"
                onClick={handleCloseModal}
                disabled={isCreating}
                leftSection={<IconX size={16} />}>
                Cancel
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={isCreating}
                className="bg-primary hover:bg-primary/90"
                leftSection={<IconPlus size={16} />}>
                {isCreating ? "Creating..." : "Create Discussion"}
              </Button>
            </Group>
          </Stack>
        </div>
      </Modal>
    </Container>
  );
}
