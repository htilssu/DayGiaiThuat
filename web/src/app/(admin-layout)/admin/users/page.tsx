import { Metadata } from "next";
import { UsersClient } from "./UsersClient";

export const metadata: Metadata = {
  title: "Quản lý người dùng - Admin Dashboard",
  description:
    "Quản lý danh sách người dùng, phân quyền và thông tin tài khoản",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["admin", "quản lý", "người dùng", "dashboard", "phân quyền"],
};

export default function UsersPage() {
  return <UsersClient />;
}
