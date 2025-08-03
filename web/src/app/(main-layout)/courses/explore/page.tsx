import { CoursesExplorePage } from "../../../../components/pages/courses/CoursesExplorePage";
import { Metadata } from "next";

export const metadata: Metadata = {
    title: "Khám phá khóa học - AI Agent Giải Thuật",
    description: "Khám phá các khóa học về giải thuật và lập trình",
    authors: [{ name: "AI Agent Giải Thuật Team" }],
    keywords: ["khóa học", "khám phá", "giải thuật", "lập trình", "học tập"],
};

/**
 * Component hiển thị trang khám phá khóa học
 */
export default function CoursesExplorePageRoute() {
    return <CoursesExplorePage />;
}
