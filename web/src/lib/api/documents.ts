import { apiClient } from "./client";

export interface Document {
  id: string;
  filename: string;
  status: "processing" | "completed" | "failed";
  createdAt: string;
  error?: string;
}

export interface UploadResponse {
  documents: Document[];
}

const documentsApi = {
  upload: async (files: File[]): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await apiClient.post<UploadResponse>(
      "/document/store",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  },

  getStatus: async (documentIds: string[]): Promise<Document[]> => {
    const response = await apiClient.get<{ documents: Document[] }>(
      "/document/status",
      {
        params: { ids: documentIds.join(",") },
      }
    );
    return response.data.documents;
  },
};

export default documentsApi;
