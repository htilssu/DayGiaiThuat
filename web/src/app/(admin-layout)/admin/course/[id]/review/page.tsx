import CourseReviewPageClient from "@/components/admin/course/CourseReviewPageClient";

interface CourseReviewPageProps {
    params: Promise<{
        id: string;
    }>;
}

export default async function CourseReviewPage({ params }: CourseReviewPageProps) {
    const { id } = await params;
    return <CourseReviewPageClient courseId={id} />;
}
