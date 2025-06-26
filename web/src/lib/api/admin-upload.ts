/**
 * API client cho admin upload
 * @module api/admin-upload
 */

import { client } from './client';

export interface FileUploadResponse {
    key: string;
    url: string;
    contentType: string;
    size: number;
}

/**
 * Upload ảnh khóa học (admin)
 * @param courseId - ID của khóa học
 * @param file - File ảnh cần upload
 * @returns Promise với thông tin file đã upload
 */
export const uploadCourseImageAdmin = async (
    courseId: number,
    file: File
): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await client.post(
        `/admin/upload/course-image/${courseId}`,
        formData,
        {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        }
    );

    return response.data;
};

/**
 * Upload ảnh khóa học tạm thời (admin) - dùng khi tạo course mới
 * @param file - File ảnh cần upload
 * @returns Promise với thông tin file đã upload
 */
export const uploadCourseImageTempAdmin = async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await client.post('/admin/upload/course-image-temp', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

export const adminUploadApi = {
    uploadCourseImageAdmin,
    uploadCourseImageTempAdmin,
}; 