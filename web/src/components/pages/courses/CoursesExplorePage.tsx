"use client";

import { CourseListItem, coursesApi } from "@/lib/api/courses";
import { useAppSelector } from "@/lib/store";
import {
  Alert,
  Badge,
  Box,
  Button,
  Card,
  Container,
  Divider,
  Grid,
  Group,
  Loader,
  Pagination,
  Select,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import {
  IconBook,
  IconClock,
  IconSearch,
  IconTrophy,
} from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";

export function CoursesExplorePage() {
  const [error, setError] = useState<string | null>(null);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [levelFilter, setLevelFilter] = useState<string | null>(null);
  const router = useRouter();
  const userState = useAppSelector((state) => state.user);

  const { data: courses, isLoading } = useQuery({
    queryKey: ["courses", currentPage],
    queryFn: async () => {
      const data = await coursesApi.getCourses(currentPage, 6);
      setTotalPages(data.totalPages);
      return data.items as CourseListItem[];
    },
    enabled: !!userState.user,
  });

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours > 0 ? `${hours} giờ ` : ""}${
      mins > 0 ? `${mins} phút` : ""
    }`;
  };

  const handleCourseClick = (courseId: number) => {
    router.push(`/courses/${courseId}`);
  };

  const handleGoToMyCourses = () => {
    router.push("/courses");
  };

  return (
    <Container size="xl" py="xl">
      <Box
        mb="xl"
        p="xl"
        className="bg-primary/90 rounded-lg text-white text-center">
        <Title order={1} mb="md" className="text-white">
          Khám phá khóa học
        </Title>
        <Text size="xl" mb="lg" style={{ color: "rgba(255, 255, 255, 0.9)" }}>
          Tìm hiểu và đăng ký các khóa học về giải thuật và lập trình
        </Text>
        {userState.user ? (
          <Button
            size="lg"
            variant="white"
            color="black"
            onClick={handleGoToMyCourses}>
            Xem khóa học của bạn
          </Button>
        ) : (
          <Button
            size="lg"
            variant="white"
            color="black"
            component="a"
            href="/auth/login">
            Đăng nhập để xem khóa học của bạn
          </Button>
        )}
      </Box>

      <Box mb="xl">
        <Grid>
          <Grid.Col span={{ base: 12, md: 8 }}>
            <TextInput
              placeholder="Tìm kiếm khóa học..."
              leftSection={<IconSearch size={16} />}
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.currentTarget.value)}
              size="md"
            />
          </Grid.Col>
          <Grid.Col span={{ base: 12, md: 4 }}>
            <Select
              placeholder="Chọn cấp độ"
              data={[
                { value: "", label: "Tất cả cấp độ" },
                { value: "Beginner", label: "Cơ bản" },
                { value: "Intermediate", label: "Trung cấp" },
                { value: "Advanced", label: "Nâng cao" },
              ]}
              value={levelFilter}
              onChange={setLevelFilter}
              clearable
              size="md"
            />
          </Grid.Col>
        </Grid>
      </Box>

      <Divider mb="xl" />

      {isLoading ? (
        <Grid>
          {[...Array(6)].map((_, i) => (
            <Grid.Col key={i} span={{ base: 12, md: 6, lg: 4 }}>
              <Card
                shadow="sm"
                padding="lg"
                radius="md"
                withBorder
                style={{ height: "400px" }}>
                <Card.Section>
                  <div style={{ height: 200, backgroundColor: "#f0f0f0" }} />
                </Card.Section>
                <Loader size="md" style={{ margin: "20px auto" }} />
              </Card>
            </Grid.Col>
          ))}
        </Grid>
      ) : error ? (
        <Alert color="red" title="Lỗi">
          {error}
        </Alert>
      ) : (
        <>
          <Grid>
            {courses?.map((course) => (
              <Grid.Col key={course.id} span={{ base: 12, md: 6, lg: 4 }}>
                <Card
                  shadow="sm"
                  padding="lg"
                  radius="md"
                  withBorder
                  style={{
                    height: "100%",
                    cursor: "pointer",
                    transition: "transform 0.2s",
                  }}
                  onClick={() => handleCourseClick(course.id)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = "translateY(-4px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = "translateY(0)";
                  }}>
                  <Card.Section>
                    <div
                      style={{
                        position: "relative",
                        height: "200px",
                        overflow: "hidden",
                      }}>
                      {course.thumbnailUrl ? (
                        <Image
                          src={course.thumbnailUrl}
                          alt={course.title}
                          fill
                          style={{ objectFit: "cover" }}
                          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                        />
                      ) : (
                        <div
                          className="w-full h-full flex items-center justify-center text-white text-5xl font-bold"
                          style={{
                            background:
                              "linear-gradient(135deg, rgb(var(--color-primary) / 0.8) 0%, rgb(var(--color-primary) / 0.9) 100%)",
                            textShadow: "0 2px 4px rgba(0,0,0,0.3)",
                          }}>
                          {course.title
                            .split(" ")
                            .slice(0, 2)
                            .map((word) => word.charAt(0).toUpperCase())
                            .join("")}
                        </div>
                      )}
                    </div>
                  </Card.Section>

                  <Box pt="md">
                    <Title order={4} lineClamp={2} mb="xs">
                      {course.title}
                    </Title>

                    <Text size="sm" c="dimmed" lineClamp={3} mb="md">
                      {course.description}
                    </Text>

                    <Group gap="xs" mb="md">
                      <Badge
                        variant="light"
                        className="text-primary border-primary/20"
                        leftSection={<IconClock size={12} />}>
                        {formatDuration(course.duration)}
                      </Badge>
                      <Badge
                        variant="light"
                        className="text-accent border-accent/20"
                        leftSection={<IconTrophy size={12} />}>
                        {course.level}
                      </Badge>
                    </Group>

                    {course.price !== undefined && (
                      <Group justify="space-between" mb="md">
                        <Text size="lg" fw={700} className="text-primary">
                          {course.price === 0
                            ? "Miễn phí"
                            : `${course.price.toLocaleString()} VNĐ`}
                        </Text>
                      </Group>
                    )}

                    <Button
                      fullWidth
                      variant="filled"
                      style={{
                        backgroundColor: "rgb(var(--color-primary))",
                        borderColor: "rgb(var(--color-primary))",
                        color: "white",
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCourseClick(course.id);
                      }}>
                      Xem chi tiết
                    </Button>
                  </Box>
                </Card>
              </Grid.Col>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box mt="xl" style={{ display: "flex", justifyContent: "center" }}>
              <Pagination
                total={totalPages}
                value={currentPage}
                onChange={handlePageChange}
                size="lg"
              />
            </Box>
          )}
        </>
      )}
    </Container>
  );
}
