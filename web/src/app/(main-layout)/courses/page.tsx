import { EnrolledCoursesPage } from "../../../components/pages/courses/EnrolledCoursesPage";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Khóa học của bạn - AI Agent Giải Thuật",
  description: "Quản lý và tiếp tục học các khóa học đã đăng ký",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
  keywords: ["khóa học", "học tập", "giải thuật", "lập trình", "tiến độ"],
};

/**
 * Component hiển thị khóa học đã đăng ký của người dùng
 */
export default function CoursesPageRoute() {
  return <EnrolledCoursesPage />;
}
