import { get, post } from "./client";

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

export const documentsApi = {
  upload: async (files: File[]): Promise<UploadResponse> => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await post<UploadResponse>(
      "/document/store",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response;
  },

  getStatus: async (documentIds: string[]): Promise<Document[]> => {
    const response = await get<Document[]>(
      "/document/status",
      {
        params: { ids: documentIds.join(",") },
      }
    );
    return response;
  },
};
