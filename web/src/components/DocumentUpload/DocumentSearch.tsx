"use client";

import { useState } from "react";
import {
  Text,
  Group,
  Stack,
  Button,
  Paper,
  TextInput,
  NumberInput,
  Card,
  Badge,
} from "@mantine/core";
import { IconSearch, IconFile, IconCalendar } from "@tabler/icons-react";
import { documentsApi, SearchResult } from "@/lib/api/documents";
import { notifications } from "@mantine/notifications";

export function DocumentSearch() {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(5);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      notifications.show({
        title: "Error",
        message: "Please enter a search query",
        color: "red",
      });
      return;
    }

    setIsSearching(true);
    try {
      const response = await documentsApi.search(query, limit);
      setResults(response.results);

      if (response.results.length === 0) {
        notifications.show({
          title: "No Results",
          message: "No documents found matching your query",
          color: "yellow",
        });
      } else {
        notifications.show({
          title: "Search Complete",
          message: `Found ${response.results.length} results`,
          color: "teal",
        });
      }
    } catch (error) {
      console.error("Error searching documents:", error);
      notifications.show({
        title: "Error",
        message: "Failed to search documents",
        color: "red",
      });
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <Stack gap="md">
      <Paper className="border border-primary/10 bg-white/50" p="md">
        <Stack gap="md">
          <Text fw={500} className="text-primary">
            Search Documents
          </Text>

          <Group gap="md" align="end">
            <TextInput
              label="Search Query"
              placeholder="Enter your search query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ flex: 1 }}
              className="text-primary"
            />

            <NumberInput
              label="Max Results"
              placeholder="5"
              value={limit}
              onChange={(value) => setLimit(typeof value === "number" ? value : Number(value) || 5)}
              min={1}
              max={20}
              style={{ width: 120 }}
              className="text-primary"
            />

            <Button
              onClick={handleSearch}
              loading={isSearching}
              disabled={!query.trim()}
              leftSection={<IconSearch size="1rem" />}
              className="bg-primary hover:bg-primary/90 text-white transition-colors">
              Search
            </Button>
          </Group>
        </Stack>
      </Paper>

      {results.length > 0 && (
        <Stack gap="md">
          <Text fw={500} className="text-primary">
            Search Results ({results.length})
          </Text>

          {results.map((result, index) => (
            <Card
              key={index}
              className="border border-primary/10 bg-white/50"
              p="md">
              <Stack gap="sm">
                <Group justify="apart" align="start">
                  <Group gap="xs">
                    <IconFile size="1.2rem" className="text-primary/70" />
                    <Text fw={500} className="text-primary">
                      {result.metadata.source || "Unknown Source"}
                    </Text>
                  </Group>

                  <Group gap="xs">
                    {result.metadata.uploaded_at && (
                      <Group gap="xs">
                        <IconCalendar size="1rem" className="text-primary/50" />
                        <Text size="sm" className="text-primary/60">
                          {new Date(
                            result.metadata.uploaded_at
                          ).toLocaleDateString()}
                        </Text>
                      </Group>
                    )}
                    <Badge variant="light" color="blue" size="sm">
                      Document ID: {result.metadata.document_id?.slice(0, 8)}...
                    </Badge>
                  </Group>
                </Group>

                <Text
                  size="sm"
                  className="text-primary/80"
                  style={{
                    maxHeight: "100px",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    display: "-webkit-box",
                    WebkitLineClamp: 4,
                    WebkitBoxOrient: "vertical",
                  }}>
                  {result.content}
                </Text>
              </Stack>
            </Card>
          ))}
        </Stack>
      )}
    </Stack>
  );
}
