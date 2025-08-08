import { Metadata } from "next";
import { Paper, Title, Text, Group, Button, Card, Stack } from "@mantine/core";
import {
  IconChartBar,
  IconMessage,
  IconUpload,
  IconUsers,
  IconArrowRight,
} from "@tabler/icons-react";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Admin Dashboard - Quản trị hệ thống",
  description: "Trang quản trị chính cho hệ thống học giải thuật",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["admin", "dashboard", "quản trị", "hệ thống", "overview"],
};

export default function AdminDashboard() {
  const adminModules = [
    {
      title: "Quản lý khóa học",
      description: "Tạo, chỉnh sửa và quản lý các khóa học",
      icon: IconChartBar,
      href: "/admin/course",
      color: "blue",
    },
    {
      title: "Quản lý topics",
      description: "Quản lý cây chủ đề và nội dung",
      icon: IconUsers,
      href: "/admin/topics",
      color: "green",
    },
    {
      title: "AI Assistant",
      description: "Trợ lý AI cho quản trị viên",
      icon: IconMessage,
      href: "/ai-assistant",
      color: "purple",
    },
    {
      title: "Upload Documents",
      description: "Quản lý và upload tài liệu cho hệ thống",
      icon: IconUpload,
      href: "/documents",
      color: "orange",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <Paper className="p-8 bg-gradient-to-r from-primary/10 to-primary/5 rounded-lg border border-primary/10">
        <div className="text-center">
          <Title order={1} className="text-3xl font-bold text-primary">
            Admin Dashboard
          </Title>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mt-4">
            Chào mừng đến với trang quản trị hệ thống. Từ đây bạn có thể quản lý
            tất cả các khía cạnh của hệ thống học giải thuật.
          </p>
        </div>
      </Paper>

      {/* Admin Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {adminModules.map((module) => (
          <Card
            key={module.href}
            className="hover:shadow-lg transition-all duration-300 border border-primary/10 hover:border-primary/30"
            component={Link}
            href={module.href}>
            <Stack gap="md" className="h-full">
              <div
                className={`w-12 h-12 rounded-lg bg-${module.color}-100 flex items-center justify-center`}>
                <module.icon size={24} className={`text-${module.color}-600`} />
              </div>

              <div className="flex-1">
                <Title order={3} className="font-semibold mb-2">
                  {module.title}
                </Title>
                <Text className="text-sm text-muted-foreground">
                  {module.description}
                </Text>
              </div>

              <Group justify="space-between" align="center">
                <Button
                  variant="light"
                  size="sm"
                  rightSection={<IconArrowRight size={16} />}
                  className={`bg-${module.color}-50 text-${module.color}-700 hover:bg-${module.color}-100`}>
                  Truy cập
                </Button>
              </Group>
            </Stack>
          </Card>
        ))}
      </div>

      {/* Quick Stats */}
      <Paper className="p-6 bg-white/50 border border-primary/10 rounded-lg">
        <Title order={3} className="mb-4">
          Thống kê nhanh
        </Title>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <Text className="text-2xl font-bold text-blue-600">1,234</Text>
            <Text className="text-sm text-muted-foreground">
              Tổng người dùng
            </Text>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <Text className="text-2xl font-bold text-green-600">56</Text>
            <Text className="text-sm text-muted-foreground">Khóa học</Text>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <Text className="text-2xl font-bold text-purple-600">89</Text>
            <Text className="text-sm text-muted-foreground">Bài học</Text>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <Text className="text-2xl font-bold text-orange-600">234</Text>
            <Text className="text-sm text-muted-foreground">Tài liệu</Text>
          </div>
        </div>
      </Paper>

      {/* Recent Activity */}
      <Paper className="p-6 bg-white/50 border border-primary/10 rounded-lg">
        <Title order={3} className="mb-4">
          Hoạt động gần đây
        </Title>
        <div className="space-y-3">
          <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <Text className="text-sm">
              Người dùng mới đăng ký: user@example.com
            </Text>
            <Text className="text-xs text-muted-foreground ml-auto">
              2 phút trước
            </Text>
          </div>
          <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <Text className="text-sm">
              Khóa học mới được tạo: &ldquo;Giải thuật cơ bản&rdquo;
            </Text>
            <Text className="text-xs text-muted-foreground ml-auto">
              15 phút trước
            </Text>
          </div>
          <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <Text className="text-sm">
              Tài liệu mới được upload: &ldquo;Data Structures.pdf&rdquo;
            </Text>
            <Text className="text-xs text-muted-foreground ml-auto">
              1 giờ trước
            </Text>
          </div>
        </div>
      </Paper>
    </div>
  );
}
