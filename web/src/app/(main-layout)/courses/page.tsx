import CoursesListPage from "@/components/courses/CoursesListPage";

export const metadata = {
  title: "Danh sách khóa học",
  description: "Khám phá các khóa học về giải thuật và lập trình",
  authors: [{ name: "AI Agent Giải Thuật Team" }],
};

/**
 * Component hiển thị danh sách khóa học
 */
export default function Page() {

  return <CoursesListPage />
}
