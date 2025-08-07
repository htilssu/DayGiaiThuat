"use client";

import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Group,
  Input,
  Modal,
  Pagination,
  Select,
  Stack,
  Table,
  Text,
  TextInput,
  Title,
  Tooltip,
} from "@mantine/core";
import {
  IconEdit,
  IconEye,
  IconSearch,
  IconTrash,
  IconUserPlus,
  IconFilter,
} from "@tabler/icons-react";
import { useEffect, useState } from "react";
import { userApi, UsersListResponse } from "@/lib/api";
import { UserData } from "@/lib/api/auth";

interface UserWithStatus extends UserData {
  status: "active" | "inactive" | "suspended";
  lastLogin?: string;
  createdAt: string;
  role: "admin" | "user" | "moderator";
}

export function UsersClient() {
  const [users, setUsers] = useState<UserWithStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [roleFilter, setRoleFilter] = useState<string>("all");
  const [selectedUser, setSelectedUser] = useState<UserWithStatus | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);

  // Mock data for demonstration
  const mockUsers: UserWithStatus[] = [
    {
      id: 1,
      email: "admin@example.com",
      username: "admin",
      avatar: "",
      fullName: "Admin User",
      status: "active",
      lastLogin: "2024-01-15T10:30:00Z",
      createdAt: "2024-01-01T00:00:00Z",
      role: "admin",
    },
    {
      id: 2,
      email: "user1@example.com",
      username: "user1",
      avatar: "",
      fullName: "John Doe",
      status: "active",
      lastLogin: "2024-01-14T15:45:00Z",
      createdAt: "2024-01-05T00:00:00Z",
      role: "user",
    },
    {
      id: 3,
      email: "moderator@example.com",
      username: "moderator",
      avatar: "",
      fullName: "Jane Smith",
      status: "active",
      lastLogin: "2024-01-13T09:20:00Z",
      createdAt: "2024-01-03T00:00:00Z",
      role: "moderator",
    },
    {
      id: 4,
      email: "inactive@example.com",
      username: "inactive_user",
      avatar: "",
      fullName: "Inactive User",
      status: "inactive",
      lastLogin: "2024-01-10T12:00:00Z",
      createdAt: "2024-01-02T00:00:00Z",
      role: "user",
    },
    {
      id: 5,
      email: "suspended@example.com",
      username: "suspended_user",
      avatar: "",
      fullName: "Suspended User",
      status: "suspended",
      lastLogin: "2024-01-08T16:30:00Z",
      createdAt: "2024-01-01T00:00:00Z",
      role: "user",
    },
  ];

  useEffect(() => {
    // Simulate API call
    setLoading(true);
    setTimeout(() => {
      setUsers(mockUsers);
      setTotalPages(1);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.username.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus =
      statusFilter === "all" || user.status === statusFilter;
    const matchesRole = roleFilter === "all" || user.role === roleFilter;

    return matchesSearch && matchesStatus && matchesRole;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "green";
      case "inactive":
        return "gray";
      case "suspended":
        return "red";
      default:
        return "gray";
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case "admin":
        return "red";
      case "moderator":
        return "blue";
      case "user":
        return "green";
      default:
        return "gray";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("vi-VN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleViewUser = (user: UserWithStatus) => {
    setSelectedUser(user);
    setShowUserModal(true);
  };

  const handleEditUser = (user: UserWithStatus) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleDeleteUser = (userId: number) => {
    if (confirm("Bạn có chắc chắn muốn xóa người dùng này?")) {
      setUsers(users.filter((user) => user.id !== userId));
    }
  };

  const handleUpdateUser = (updatedUser: UserWithStatus) => {
    setUsers(
      users.map((user) => (user.id === updatedUser.id ? updatedUser : user))
    );
    setShowEditModal(false);
    setSelectedUser(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <Text className="mt-4 text-muted-foreground">
            Đang tải dữ liệu...
          </Text>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <Title order={2} className="font-bold">
            Quản lý người dùng
          </Title>
          <Text className="text-muted-foreground mt-1">
            Quản lý danh sách người dùng và phân quyền
          </Text>
        </div>
        <Button
          leftSection={<IconUserPlus size={16} />}
          className="bg-primary hover:bg-primary/90">
          Thêm người dùng
        </Button>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <TextInput
            placeholder="Tìm kiếm người dùng..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            leftSection={<IconSearch size={16} />}
            className="md:col-span-2"
          />
          <Select
            placeholder="Trạng thái"
            value={statusFilter}
            onChange={(value) => setStatusFilter(value || "all")}
            data={[
              { value: "all", label: "Tất cả trạng thái" },
              { value: "active", label: "Hoạt động" },
              { value: "inactive", label: "Không hoạt động" },
              { value: "suspended", label: "Bị đình chỉ" },
            ]}
            leftSection={<IconFilter size={16} />}
          />
          <Select
            placeholder="Vai trò"
            value={roleFilter}
            onChange={(value) => setRoleFilter(value || "all")}
            data={[
              { value: "all", label: "Tất cả vai trò" },
              { value: "admin", label: "Quản trị viên" },
              { value: "moderator", label: "Điều hành viên" },
              { value: "user", label: "Người dùng" },
            ]}
            leftSection={<IconFilter size={16} />}
          />
        </div>
      </Card>

      {/* Users Table */}
      <Card className="p-0">
        <div className="overflow-x-auto">
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Người dùng</Table.Th>
                <Table.Th>Email</Table.Th>
                <Table.Th>Vai trò</Table.Th>
                <Table.Th>Trạng thái</Table.Th>
                <Table.Th>Đăng nhập cuối</Table.Th>
                <Table.Th>Ngày tạo</Table.Th>
                <Table.Th className="text-right">Thao tác</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {filteredUsers.map((user) => (
                <Table.Tr key={user.id}>
                  <Table.Td>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Text className="font-semibold text-primary">
                          {user.fullName.charAt(0).toUpperCase()}
                        </Text>
                      </div>
                      <div>
                        <Text className="font-medium">{user.fullName}</Text>
                        <Text className="text-sm text-muted-foreground">
                          @{user.username}
                        </Text>
                      </div>
                    </div>
                  </Table.Td>
                  <Table.Td>
                    <Text className="text-sm">{user.email}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={getRoleColor(user.role)} variant="light">
                      {user.role === "admin"
                        ? "Quản trị viên"
                        : user.role === "moderator"
                        ? "Điều hành viên"
                        : "Người dùng"}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Badge color={getStatusColor(user.status)} variant="light">
                      {user.status === "active"
                        ? "Hoạt động"
                        : user.status === "inactive"
                        ? "Không hoạt động"
                        : "Bị đình chỉ"}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text className="text-sm text-muted-foreground">
                      {user.lastLogin
                        ? formatDate(user.lastLogin)
                        : "Chưa đăng nhập"}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text className="text-sm text-muted-foreground">
                      {formatDate(user.createdAt)}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Group gap="xs" justify="flex-end">
                      <Tooltip label="Xem chi tiết">
                        <ActionIcon
                          variant="light"
                          size="sm"
                          onClick={() => handleViewUser(user)}
                          className="text-blue-600 hover:bg-blue-50">
                          <IconEye size={16} />
                        </ActionIcon>
                      </Tooltip>
                      <Tooltip label="Chỉnh sửa">
                        <ActionIcon
                          variant="light"
                          size="sm"
                          onClick={() => handleEditUser(user)}
                          className="text-orange-600 hover:bg-orange-50">
                          <IconEdit size={16} />
                        </ActionIcon>
                      </Tooltip>
                      <Tooltip label="Xóa">
                        <ActionIcon
                          variant="light"
                          size="sm"
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:bg-red-50">
                          <IconTrash size={16} />
                        </ActionIcon>
                      </Tooltip>
                    </Group>
                  </Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </div>

        {filteredUsers.length === 0 && (
          <div className="text-center py-12">
            <Text className="text-muted-foreground">
              Không tìm thấy người dùng nào
            </Text>
          </div>
        )}
      </Card>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center">
          <Pagination
            total={totalPages}
            value={currentPage}
            onChange={setCurrentPage}
            className="mt-6"
          />
        </div>
      )}

      {/* User Detail Modal */}
      <Modal
        opened={showUserModal}
        onClose={() => setShowUserModal(false)}
        title="Chi tiết người dùng"
        size="lg">
        {selectedUser && (
          <Stack gap="md">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                <Text className="font-semibold text-primary text-xl">
                  {selectedUser.fullName.charAt(0).toUpperCase()}
                </Text>
              </div>
              <div>
                <Title order={4}>{selectedUser.fullName}</Title>
                <Text className="text-muted-foreground">
                  @{selectedUser.username}
                </Text>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Text className="text-sm font-medium text-muted-foreground">
                  Email
                </Text>
                <Text>{selectedUser.email}</Text>
              </div>
              <div>
                <Text className="text-sm font-medium text-muted-foreground">
                  Vai trò
                </Text>
                <Badge color={getRoleColor(selectedUser.role)} variant="light">
                  {selectedUser.role === "admin"
                    ? "Quản trị viên"
                    : selectedUser.role === "moderator"
                    ? "Điều hành viên"
                    : "Người dùng"}
                </Badge>
              </div>
              <div>
                <Text className="text-sm font-medium text-muted-foreground">
                  Trạng thái
                </Text>
                <Badge
                  color={getStatusColor(selectedUser.status)}
                  variant="light">
                  {selectedUser.status === "active"
                    ? "Hoạt động"
                    : selectedUser.status === "inactive"
                    ? "Không hoạt động"
                    : "Bị đình chỉ"}
                </Badge>
              </div>
              <div>
                <Text className="text-sm font-medium text-muted-foreground">
                  Đăng nhập cuối
                </Text>
                <Text className="text-sm">
                  {selectedUser.lastLogin
                    ? formatDate(selectedUser.lastLogin)
                    : "Chưa đăng nhập"}
                </Text>
              </div>
            </div>

            <div>
              <Text className="text-sm font-medium text-muted-foreground">
                Ngày tạo tài khoản
              </Text>
              <Text className="text-sm">
                {formatDate(selectedUser.createdAt)}
              </Text>
            </div>
          </Stack>
        )}
      </Modal>

      {/* Edit User Modal */}
      <Modal
        opened={showEditModal}
        onClose={() => setShowEditModal(false)}
        title="Chỉnh sửa người dùng"
        size="md">
        {selectedUser && (
          <Stack gap="md">
            <TextInput
              label="Họ và tên"
              value={selectedUser.fullName}
              onChange={(e) =>
                setSelectedUser({
                  ...selectedUser,
                  fullName: e.target.value,
                })
              }
            />
            <TextInput
              label="Email"
              value={selectedUser.email}
              onChange={(e) =>
                setSelectedUser({
                  ...selectedUser,
                  email: e.target.value,
                })
              }
            />
            <TextInput
              label="Tên đăng nhập"
              value={selectedUser.username}
              onChange={(e) =>
                setSelectedUser({
                  ...selectedUser,
                  username: e.target.value,
                })
              }
            />
            <Select
              label="Vai trò"
              value={selectedUser.role}
              onChange={(value) =>
                setSelectedUser({
                  ...selectedUser,
                  role: (value as "admin" | "user" | "moderator") || "user",
                })
              }
              data={[
                { value: "user", label: "Người dùng" },
                { value: "moderator", label: "Điều hành viên" },
                { value: "admin", label: "Quản trị viên" },
              ]}
            />
            <Select
              label="Trạng thái"
              value={selectedUser.status}
              onChange={(value) =>
                setSelectedUser({
                  ...selectedUser,
                  status:
                    (value as "active" | "inactive" | "suspended") || "active",
                })
              }
              data={[
                { value: "active", label: "Hoạt động" },
                { value: "inactive", label: "Không hoạt động" },
                { value: "suspended", label: "Bị đình chỉ" },
              ]}
            />

            <Group justify="flex-end" gap="sm">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>
                Hủy
              </Button>
              <Button
                onClick={() => handleUpdateUser(selectedUser)}
                className="bg-primary hover:bg-primary/90">
                Cập nhật
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </div>
  );
}
