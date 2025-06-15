import { get } from "./client";

export interface ProfileData {
    id: number;
    email: string;
    username: string;
    fullName: string;
    avatar: string;
}

export const profileApi = {
    getProfile: async (): Promise<ProfileData> => {
        const response = await get<ProfileData>("/profile");
        return response;
    }
};

