import { CourseListItem, coursesApi } from "@/lib/api";
import { useAppSelector } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";

/**
 * Component hiển thị danh sách khóa học
 */
export default function Page() {

  return <CoursesListPage />
}
