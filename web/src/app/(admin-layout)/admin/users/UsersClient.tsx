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
  Notification,
} from "@mantine/core";
import {
  IconEdit,
  IconEye,
  IconSearch,
  IconTrash,
  IconUserPlus,
  IconFilter,
  IconCheck,
  IconX,
} from "@tabler/icons-react";
import { useEffect, useState } from "react";
import {
  userApi,
  AdminUserResponse,
  AdminUserUpdate,
  AdminUserCreate,
} from "@/lib/api";
import { useAppSelector } from "@/lib/store";

interface UserWithStatus extends AdminUserResponse {
  status: "active" | "inactive";
  lastLogin?: string;
  role: "admin" | "user";
  fullName: string;
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
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [notification, setNotification] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  // Get current user from store
  const currentUser = useAppSelector((state) => state.user.user);

  // Load users from API
  const loadUsers = async () => {
    try {
      setLoading(true);
      console.log("Loading users from API...");
      const usersData = await userApi.getAllUsersAdmin();
      console.log("Users data received:", usersData);

      const transformedUsers: UserWithStatus[] = usersData.map((user) => ({
        ...user,
        fullName: `${user.firstName || ""} ${user.lastName || ""}`.trim(),
        status: user.isActive ? "active" : "inactive",
        role: user.isAdmin ? "admin" : "user",
        lastLogin: undefined, // Not available in current API
      }));

      setUsers(transformedUsers);
      setTotalPages(Math.ceil(transformedUsers.length / 10));
    } catch (error) {
      console.error("Error loading users:", error);
      // Show more detailed error information
      const errorMessage =
        error instanceof Error
          ? error.message
          : "Không thể tải danh sách người dùng";
      setNotification({
        type: "error",
        message: `Lỗi: ${errorMessage}. Có thể bạn không có quyền admin hoặc chưa đăng nhập.`,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
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

  const getStatusColor = (status: boolean) => {
    switch (status) {
      case true:
        return "green";
      case false:
        return "gray";
      default:
        return "gray";
    }
  };

  const getRoleColor = (role: boolean) => {
    switch (role) {
      case true:
        return "red";
      case false:
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

  const handleDeleteUser = async (userId: number) => {
    if (confirm("Bạn có chắc chắn muốn xóa người dùng này?")) {
      try {
        await userApi.deleteUserAdmin(userId);
        setUsers(users.filter((user) => user.id !== userId));
        setNotification({
          type: "success",
          message: "Xóa người dùng thành công",
        });
      } catch (error) {
        console.error("Error deleting user:", error);
        setNotification({
          type: "error",
          message: "Không thể xóa người dùng",
        });
      }
    }
  };

  const handleUpdateUser = async (updatedUser: UserWithStatus) => {
    try {
      const updateData: AdminUserUpdate = {
        email: updatedUser.email,
        username: updatedUser.username,
        firstName: updatedUser.firstName,
        lastName: updatedUser.lastName,
        isAdmin: updatedUser.isAdmin,
        isActive: updatedUser.isActive,
        bio: updatedUser.bio,
        avatarUrl: updatedUser.avatarUrl,
      };

      await userApi.updateUserAdmin(updatedUser.id, updateData);

      setUsers(
        users.map((user) => (user.id === updatedUser.id ? updatedUser : user))
      );
      setShowEditModal(false);
      setSelectedUser(null);
      setNotification({
        type: "success",
        message: "Cập nhật người dùng thành công",
      });
    } catch (error) {
      console.error("Error updating user:", error);
      setNotification({
        type: "error",
        message: "Không thể cập nhật người dùng",
      });
    }
  };

  const handleCreateUser = async (userData: AdminUserCreate) => {
    try {
      const newUser = await userApi.createUserAdmin(userData);

      // Transform the new user to match our interface
      const transformedUser: UserWithStatus = {
        ...newUser,
        status: newUser.isActive ? "active" : "inactive",
        role: newUser.isAdmin ? "admin" : "user",
        lastLogin: undefined,
        fullName: `${newUser.firstName || ""} ${newUser.lastName || ""}`.trim(),
      };

      setUsers([...users, transformedUser]);
      setShowCreateModal(false);
      setNotification({
        type: "success",
        message: "Tạo người dùng thành công",
      });
    } catch (error) {
      console.error("Error creating user:", error);
      setNotification({
        type: "error",
        message: "Không thể tạo người dùng",
      });
    }
  };

  const handleToggleUserStatus = async (userId: number, isActive: boolean) => {
    try {
      if (isActive) {
        await userApi.activateUserAdmin(userId);
      } else {
        await userApi.deactivateUserAdmin(userId);
      }

      setUsers(
        users.map((user) =>
          user.id === userId
            ? {
              ...user,
              is_active: isActive,
              status: isActive ? "active" : "inactive",
            }
            : user
        )
      );

      setNotification({
        type: "success",
        message: isActive
          ? "Kích hoạt người dùng thành công"
          : "Vô hiệu hóa người dùng thành công",
      });
    } catch (error) {
      console.error("Error toggling user status:", error);
      setNotification({
        type: "error",
        message: "Không thể thay đổi trạng thái người dùng",
      });
    }
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

  // Show error state if no users and there was an error
  if (users.length === 0 && notification?.type === "error") {
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
        </div>

        {/* Error State */}
        <Card className="p-6">
          <div className="text-center py-12">
            <div className="text-red-500 mb-4">
              <IconX size={48} className="mx-auto" />
            </div>
            <Title order={3} className="mb-2">
              Không thể tải dữ liệu người dùng
            </Title>
            <Text className="text-muted-foreground mb-4">
              {notification?.message}
            </Text>
            <Text className="text-sm text-muted-foreground">
              Vui lòng kiểm tra:
            </Text>
            <ul className="text-sm text-muted-foreground mt-2 space-y-1">
              <li>• Bạn đã đăng nhập với tài khoản có quyền admin</li>
              <li>• Kết nối mạng và máy chủ hoạt động bình thường</li>
              <li>• Cookie phiên đăng nhập còn hiệu lực</li>
            </ul>
            {currentUser && (
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <Text className="text-sm text-blue-700">
                  <strong>Thông tin người dùng hiện tại:</strong>
                  <br />
                  Email: {currentUser.email}
                  <br />
                  Username: {currentUser.username}
                  <br />
                  <span className="text-red-600">
                    ⚠️ Tài khoản này có thể không có quyền admin
                  </span>
                </Text>
              </div>
            )}
            <Button
              onClick={loadUsers}
              className="mt-4 bg-primary hover:bg-primary/90">
              Thử lại
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Notification */}
      {notification && (
        <Notification
          icon={
            notification.type === "success" ? (
              <IconCheck size={16} />
            ) : (
              <IconX size={16} />
            )
          }
          color={notification.type === "success" ? "green" : "red"}
          onClose={() => setNotification(null)}
          className="mb-4">
          {notification.message}
        </Notification>
      )}

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
          className="bg-primary hover:bg-primary/90"
          onClick={() => setShowCreateModal(true)}>
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
              { value: "user", label: "Người dùng" },
            ]}
            leftSection={<IconFilter size={16} />}
          />
        </div>
      </Card>

      {/* Users Table */}
      <Card className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="h-10">
                <th className="text-center">Người dùng</th>
                <th className="text-center">Email</th>
                <th className="text-center">Vai trò</th>
                <th className="text-center">Trạng thái</th>
                <th className="text-center">Ngày tạo</th>
                <th className="text-center">Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.map((user) => (
                <tr key={user.id}>
                  <td className="h-10">
                    @{user.username}
                  </td>
                  <td>
                    <Text className="text-sm">{user.email}</Text>
                  </td>
                  <td className="text-center">
                    <Badge color={getRoleColor(user.isAdmin)} variant="light">
                      {user.isAdmin ? "Quản trị viên" : "Người dùng"}
                    </Badge>
                  </td>
                  <td className="text-center">
                    <Badge
                      color={getStatusColor(user.isActive)}
                      variant="light">
                      {user.isActive ? "Hoạt động" : "Không hoạt động"}
                    </Badge>
                  </td>
                  <td className="text-center">
                    <Text className="text-sm text-muted-foreground">
                      {formatDate(user.createdAt)}
                    </Text>
                  </td>
                  <td className="flex justify-center">
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
                      <Tooltip
                        label={user.isActive ? "Vô hiệu hóa" : "Kích hoạt"}>
                        <ActionIcon
                          variant="light"
                          size="sm"
                          onClick={() =>
                            handleToggleUserStatus(user.id, !user.isActive)
                          }
                          className={
                            user.isActive
                              ? "text-yellow-600 hover:bg-yellow-50"
                              : "text-green-600 hover:bg-green-50"
                          }>
                          {user.isActive ? "🚫" : "✅"}
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
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
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
                <Badge
                  color={getRoleColor(selectedUser.isAdmin)}
                  variant="light">
                  {selectedUser.isAdmin ? "Quản trị viên" : "Người dùng"}
                </Badge>
              </div>
              <div>
                <Text className="text-sm font-medium text-muted-foreground">
                  Trạng thái
                </Text>
                <Badge
                  color={getStatusColor(selectedUser.isActive)}
                  variant="light">
                  {selectedUser.isActive ? "Hoạt động" : "Không hoạt động"}
                </Badge>
              </div>
              <div>
                <Text className="text-sm font-medium text-muted-foreground">
                  Ngày tạo
                </Text>
                <Text className="text-sm">
                  {formatDate(selectedUser.createdAt)}
                </Text>
              </div>
            </div>

            {selectedUser.bio && (
              <div>
                <Text className="text-sm font-medium text-muted-foreground">
                  Giới thiệu
                </Text>
                <Text className="text-sm">{selectedUser.bio}</Text>
              </div>
            )}
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
              value={`${selectedUser.firstName} ${selectedUser.lastName}`}
              onChange={(e) => {
                const names = e.target.value.split(" ");
                const firstName = names[0] || "";
                const lastName = names.slice(1).join(" ") || "";
                setSelectedUser({
                  ...selectedUser,
                  firstName: firstName,
                  lastName: lastName,
                  fullName: e.target.value,
                });
              }}
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
                  role: (value as "admin" | "user") || "user",
                  isAdmin: value === "admin",
                })
              }
              data={[
                { value: "user", label: "Người dùng" },
                { value: "admin", label: "Quản trị viên" },
              ]}
            />
            <Select
              label="Trạng thái"
              value={selectedUser.status}
              onChange={(value) =>
                setSelectedUser({
                  ...selectedUser,
                  status: (value as "active" | "inactive") || "active",
                  isActive: value === "active",
                })
              }
              data={[
                { value: "active", label: "Hoạt động" },
                { value: "inactive", label: "Không hoạt động" },
              ]}
            />
            <TextInput
              label="Giới thiệu"
              value={selectedUser.bio || ""}
              onChange={(e) =>
                setSelectedUser({
                  ...selectedUser,
                  bio: e.target.value,
                })
              }
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

      {/* Create User Modal */}
      <Modal
        opened={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Thêm người dùng mới"
        size="md">
        <CreateUserForm
          onSubmit={handleCreateUser}
          onCancel={() => setShowCreateModal(false)}
        />
      </Modal>
    </div>
  );
}

// Create User Form Component
interface CreateUserFormProps {
  onSubmit: (userData: AdminUserCreate) => void;
  onCancel: () => void;
}

function CreateUserForm({ onSubmit, onCancel }: CreateUserFormProps) {
  const [formData, setFormData] = useState<AdminUserCreate>({
    email: "",
    username: "",
    password: "",
    firstName: "",
    lastName: "",
    isAdmin: false,
    isActive: true,
    bio: "",
    avatarUrl: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <Stack gap="md">
        <TextInput
          label="Email"
          required
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />
        <TextInput
          label="Tên đăng nhập"
          required
          value={formData.username}
          onChange={(e) =>
            setFormData({ ...formData, username: e.target.value })
          }
        />
        <TextInput
          label="Mật khẩu"
          type="password"
          required
          value={formData.password}
          onChange={(e) =>
            setFormData({ ...formData, password: e.target.value })
          }
        />
        <TextInput
          label="Họ"
          required
          value={formData.firstName}
          onChange={(e) =>
            setFormData({ ...formData, firstName: e.target.value })
          }
        />
        <TextInput
          label="Tên"
          required
          value={formData.lastName}
          onChange={(e) =>
            setFormData({ ...formData, lastName: e.target.value })
          }
        />
        <Select
          label="Vai trò"
          value={formData.isAdmin ? "admin" : "user"}
          onChange={(value) =>
            setFormData({
              ...formData,
              isAdmin: value === "admin",
            })
          }
          data={[
            { value: "user", label: "Người dùng" },
            { value: "admin", label: "Quản trị viên" },
          ]}
        />
        <Select
          label="Trạng thái"
          value={formData.isActive ? "active" : "inactive"}
          onChange={(value) =>
            setFormData({
              ...formData,
              isActive: value === "active",
            })
          }
          data={[
            { value: "active", label: "Hoạt động" },
            { value: "inactive", label: "Không hoạt động" },
          ]}
        />
        <TextInput
          label="Giới thiệu"
          value={formData.bio}
          onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
        />

        <Group justify="flex-end" gap="sm">
          <Button variant="outline" onClick={onCancel}>
            Hủy
          </Button>
          <Button type="submit" className="bg-primary hover:bg-primary/90">
            Tạo người dùng
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
