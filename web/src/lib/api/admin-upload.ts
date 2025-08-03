/**
 * API client cho admin upload files
 * @module api/admin-upload
 */

import { post } from "./client";

export interface AdminFileUploadResponse {
    key: string;
    url: string;
    content_type: string;
    size: number;
}

/**
 * Upload image cho khóa học (admin)
 * @param courseId - ID của khóa học
 * @param file - File image cần upload
 * @returns Kết quả upload
 */
export const uploadCourseImageAdmin = async (
    courseId: number,
    file: File
): Promise<AdminFileUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    return post<AdminFileUploadResponse>(
        `/admin/upload/course-image/${courseId}`,
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );
};

/**
 * Upload image tạm thời cho khóa học (admin)
 * @param file - File image cần upload
 * @returns Kết quả upload
 */
export const uploadCourseImageTempAdmin = async (file: File): Promise<AdminFileUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    return post<AdminFileUploadResponse>(`/admin/upload/course-image-temp`, formData, {
        headers: {
            "Content-Type": "multipart/form-data",
        },
    });
};

export const adminUploadApi = {
    uploadCourseImageAdmin,
    uploadCourseImageTempAdmin,
}; 