export interface Discussion {
    id: string;
    title: string;
    content: string;
    author: string;
    category: string;
    createdAt: string;
    replies: number;
}

export interface DiscussionsResponse {
    discussions: Discussion[];
    totalPages: number;
    currentPage: number;
    total: number;
}

export interface GetDiscussionsParams {
    search?: string;
    sortBy?: "newest" | "oldest" | "most-replies";
    page?: number;
    limit?: number;
}

export const discussionsApi = {
    getDiscussions: async (params: GetDiscussionsParams): Promise<DiscussionsResponse> => {
        // Mock data
        const mockDiscussions: Discussion[] = [
            {
                id: "1",
                title: "Hỏi về thuật toán sắp xếp nào tốt nhất?",
                content: "Tôi đang học về các thuật toán sắp xếp...",
                author: "Nguyễn Văn A",
                category: "Thuật toán",
                createdAt: new Date().toISOString(),
                replies: 5
            },
            {
                id: "2",
                title: "Làm thế nào để tối ưu hóa code Python?",
                content: "Cần lời khuyên về việc tối ưu hóa code...",
                author: "Trần Thị B",
                category: "Python",
                createdAt: new Date().toISOString(),
                replies: 3
            }
        ];

        return Promise.resolve({
            discussions: mockDiscussions,
            totalPages: 1,
            currentPage: 1,
            total: mockDiscussions.length
        });
    },

    getDiscussion: async (id: string): Promise<Discussion> => {
        const mockDiscussion: Discussion = {
            id,
            title: `Thảo luận ${id}`,
            content: "Nội dung thảo luận...",
            author: "User",
            category: "General",
            createdAt: new Date().toISOString(),
            replies: 0
        };

        return Promise.resolve(mockDiscussion);
    }
}; 