import { discussions } from "@/data/discussions";
import { notFound } from "next/navigation";
import { Suspense } from "react";
import DiscussionDetailClient from "@/components/discussions/DiscussionDetailClient";
import LoadingSpinner from "@/components/ui/LoadingSpinner";

interface Props {
  params: Promise<{ id: string }>;
}

export default async function DiscussionDetailPage({ params }: Props) {
  const { id: idParam } = await params;
  const id = Number(idParam);
  const discussion = discussions.find((d) => d.id === id);

  if (!discussion) return notFound();

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <DiscussionDetailClient id={id} />
    </Suspense>
  );
}
