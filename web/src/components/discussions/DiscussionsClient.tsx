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
} from "@mantine/core";
import {
    IconSearch,
    IconPlus,
    IconMessageCircle,
    IconCalendar,
} from "@tabler/icons-react";
import { useDiscussions } from "@/hooks/useDiscussions";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function DiscussionsClient() {
    const router = useRouter();
    const [searchTerm, setSearchTerm] = useState("");
    const [sortBy, setSortBy] = useState<string>("newest");
    const [categoryFilter, setCategoryFilter] = useState<string>("all");
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 10;

    // Use React Query to fetch discussions
    const {
        data: discussionsData,
        isLoading: loading,
        error,
        refetch
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
        router.push("/discussions/new");
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
    const categories = Array.from(
        new Set(discussions.map((d) => d.category))
    );

    if (error) {
        return (
            <Container size="lg" py="xl">
                <Card withBorder className="bg-background/50 border-foreground/10 theme-transition p-6">
                    <Text className="text-foreground">Error loading discussions. Please try again.</Text>
                    <Button onClick={() => refetch()} mt="md" className="bg-primary hover:bg-primary/90">
                        Retry
                    </Button>
                </Card>
            </Container>
        );
    }

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
                    New Discussion
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
                                if (event.key === 'Enter') {
                                    handleSearch();
                                }
                            }}
                        />
                        <Button
                            onClick={handleSearch}
                            className="bg-primary hover:bg-primary/90"
                        >
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
        </Container>
    );
}
