import { client } from './client';

export interface FileUploadResponse {
    key: string;
    url: string;
    contentType: string;
    size: number;
}

/**
 * Upload avatar người dùng
 * @param file - File ảnh cần upload
 * @returns Promise với thông tin file đã upload
 */
export const uploadUserAvatar = async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await client.post('/upload/user-avatar', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

export const uploadApi = {
    uploadUserAvatar,
}; 