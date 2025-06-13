import { apiClient as client } from "./client";

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

    const response = await client.post<UploadResponse>(
      "/api/documents/upload",
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
    const response = await client.get<{ documents: Document[] }>(
      "/api/documents/status",
      {
        params: { ids: documentIds.join(",") },
      }
    );
    return response.data.documents;
  },
};

export default documentsApi;
