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
import { discussions as mockDiscussions } from "@/data/discussions";
import Link from "next/link";

export default function DiscussionsClient() {
    const router = useRouter();
    const [discussions, setDiscussions] = useState<Discussion[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [sortBy, setSortBy] = useState<string>("newest");
    const [categoryFilter, setCategoryFilter] = useState<string>("all");
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 10;

    useEffect(() => {
        const fetchDiscussions = async () => {
            try {
                setLoading(true);
                // For now, using mock data
                setDiscussions(
                    mockDiscussions.map(discussion => ({
                        ...discussion,
                        id: String(discussion.id),
                    }))
                );
            } catch (error) {
                console.error("Error fetching discussions:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDiscussions();
    }, []);

    const handleCreateNew = () => {
        router.push("/discussions/new");
    };

    // Filter and sort discussions
    const filteredDiscussions = discussions
        .filter((discussion) => {
            const matchesSearch = discussion.title
                .toLowerCase()
                .includes(searchTerm.toLowerCase());
            const matchesCategory =
                categoryFilter === "all" || discussion.category === categoryFilter;
            return matchesSearch && matchesCategory;
        })
        .sort((a, b) => {
            switch (sortBy) {
                case "newest":
                    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
                case "oldest":
                    return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
                case "replies":
                    return b.replies - a.replies;
                default:
                    return 0;
            }
        });

    // Pagination
    const totalPages = Math.ceil(filteredDiscussions.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const paginatedDiscussions = filteredDiscussions.slice(
        startIndex,
        startIndex + itemsPerPage
    );

    const categories = Array.from(
        new Set(discussions.map((d) => d.category))
    );

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
                    <TextInput
                        placeholder="Search discussions..."
                        leftSection={<IconSearch size={16} />}
                        value={searchTerm}
                        onChange={(event) => setSearchTerm(event.currentTarget.value)}
                        className="flex-1"
                    />
                    <Group>
                        <Select
                            placeholder="Sort by"
                            value={sortBy}
                            onChange={(value) => setSortBy(value || "newest")}
                            data={[
                                { value: "newest", label: "Newest" },
                                { value: "oldest", label: "Oldest" },
                                { value: "replies", label: "Most Replies" },
                            ]}
                            className="min-w-[150px]"
                        />
                        <Select
                            placeholder="Category"
                            value={categoryFilter}
                            onChange={(value) => setCategoryFilter(value || "all")}
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
                    {paginatedDiscussions.length === 0 ? (
                        <Card withBorder className="border-border">
                            <Text ta="center" py="xl" className="text-muted-foreground">
                                No discussions found.
                            </Text>
                        </Card>
                    ) : (
                        <Stack gap="md">
                            {paginatedDiscussions.map((discussion) => (
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
