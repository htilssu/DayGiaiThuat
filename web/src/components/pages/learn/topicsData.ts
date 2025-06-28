// Định nghĩa các kiểu dữ liệu
export interface UITopic {
    id: string;
    title: string;
    description: string;
    icon: string;
    color: string;
    progress: number;
    totalLessons: number;
    completedLessons: number;
    isLocked: boolean;
    prerequisites?: string[];
    lessons?: TopicLesson[];
}

export interface TopicLesson {
    id: string;
    title: string;
    isCompleted: boolean;
}

// Dữ liệu mẫu cho các chủ đề
export const topicsData: UITopic[] = [
    {
        id: "algorithms-basics",
        title: "Cơ bản về giải thuật",
        description: "Tìm hiểu về các khái niệm cơ bản, độ phức tạp và cách phân tích giải thuật",
        icon: "📊",
        color: "primary",
        progress: 50,
        totalLessons: 5,
        completedLessons: 2,
        isLocked: false,
        lessons: [
            {
                id: "1",
                title: "Giới thiệu về Giải thuật",
                isCompleted: true
            },
            {
                id: "2",
                title: "Độ phức tạp của giải thuật",
                isCompleted: true
            },
            {
                id: "3",
                title: "Phân tích giải thuật",
                isCompleted: false
            },
            {
                id: "4",
                title: "Kỹ thuật thiết kế giải thuật",
                isCompleted: false
            },
            {
                id: "5",
                title: "Đánh giá hiệu suất giải thuật",
                isCompleted: false
            }
        ]
    },
    {
        id: "data-structures",
        title: "Cấu trúc dữ liệu",
        description: "Học về các cấu trúc dữ liệu phổ biến như mảng, danh sách liên kết, ngăn xếp, hàng đợi",
        icon: "🧩",
        color: "secondary",
        progress: 20,
        totalLessons: 5,
        completedLessons: 1,
        isLocked: false,
        prerequisites: ["algorithms-basics"],
        lessons: [
            {
                id: "1",
                title: "Giới thiệu về Cấu trúc dữ liệu",
                isCompleted: true
            },
            {
                id: "2",
                title: "Mảng và Danh sách",
                isCompleted: false
            },
            {
                id: "3",
                title: "Ngăn xếp và Hàng đợi",
                isCompleted: false
            },
            {
                id: "4",
                title: "Cây và Đồ thị",
                isCompleted: false
            },
            {
                id: "5",
                title: "Bảng băm",
                isCompleted: false
            }
        ]
    },
    {
        id: "sorting-algorithms",
        title: "Giải thuật sắp xếp",
        description: "Tìm hiểu về các thuật toán sắp xếp như Bubble Sort, Quick Sort, Merge Sort và nhiều thuật toán khác",
        icon: "🔄",
        color: "accent",
        progress: 0,
        totalLessons: 6,
        completedLessons: 0,
        isLocked: true,
        prerequisites: ["algorithms-basics", "data-structures"],
        lessons: [
            {
                id: "1",
                title: "Giới thiệu về Giải thuật sắp xếp",
                isCompleted: false
            },
            {
                id: "2",
                title: "Bubble Sort và Selection Sort",
                isCompleted: false
            },
            {
                id: "3",
                title: "Insertion Sort",
                isCompleted: false
            },
            {
                id: "4",
                title: "Merge Sort",
                isCompleted: false
            },
            {
                id: "5",
                title: "Quick Sort",
                isCompleted: false
            },
            {
                id: "6",
                title: "Heap Sort và Counting Sort",
                isCompleted: false
            }
        ]
    },
    {
        id: "searching-algorithms",
        title: "Giải thuật tìm kiếm",
        description: "Tìm hiểu về các thuật toán tìm kiếm như Linear Search, Binary Search và các biến thể",
        icon: "🔍",
        color: "warning",
        progress: 0,
        totalLessons: 4,
        completedLessons: 0,
        isLocked: true,
        prerequisites: ["algorithms-basics", "data-structures"],
        lessons: [
            {
                id: "1",
                title: "Giới thiệu về Giải thuật tìm kiếm",
                isCompleted: false
            },
            {
                id: "2",
                title: "Linear Search",
                isCompleted: false
            },
            {
                id: "3",
                title: "Binary Search",
                isCompleted: false
            },
            {
                id: "4",
                title: "Các biến thể của Binary Search",
                isCompleted: false
            }
        ]
    },
    {
        id: "dynamic-programming",
        title: "Quy hoạch động",
        description: "Học cách giải quyết các bài toán phức tạp bằng phương pháp quy hoạch động",
        icon: "📈",
        color: "success",
        progress: 0,
        totalLessons: 5,
        completedLessons: 0,
        isLocked: true,
        prerequisites: ["algorithms-basics", "data-structures"],
        lessons: [
            {
                id: "1",
                title: "Giới thiệu về Quy hoạch động",
                isCompleted: false
            },
            {
                id: "2",
                title: "Bài toán dãy con tăng dài nhất",
                isCompleted: false
            },
            {
                id: "3",
                title: "Bài toán cái túi",
                isCompleted: false
            },
            {
                id: "4",
                title: "Bài toán tối ưu hóa",
                isCompleted: false
            },
            {
                id: "5",
                title: "Thực hành với các bài toán phức tạp",
                isCompleted: false
            }
        ]
    },
    {
        id: "graph-algorithms",
        title: "Giải thuật đồ thị",
        description: "Tìm hiểu về các thuật toán trên đồ thị như BFS, DFS, Dijkstra, Floyd-Warshall",
        icon: "🔗",
        color: "error",
        progress: 0,
        totalLessons: 6,
        completedLessons: 0,
        isLocked: true,
        prerequisites: ["algorithms-basics", "data-structures"],
        lessons: [
            {
                id: "1",
                title: "Giới thiệu về Đồ thị",
                isCompleted: false
            },
            {
                id: "2",
                title: "BFS và DFS",
                isCompleted: false
            },
            {
                id: "3",
                title: "Thuật toán Dijkstra",
                isCompleted: false
            },
            {
                id: "4",
                title: "Thuật toán Floyd-Warshall",
                isCompleted: false
            },
            {
                id: "5",
                title: "Cây khung nhỏ nhất",
                isCompleted: false
            },
            {
                id: "6",
                title: "Thuật toán dòng chảy tối đa",
                isCompleted: false
            }
        ]
    }
];

// Hàm tiện ích để tìm bài học
export function getLesson(topicId: string, lessonId: string): TopicLesson | null {
    const topic = topicsData.find(t => t.id === topicId);
    if (!topic || !topic.lessons) return null;

    return topic.lessons.find(lesson => lesson.id === lessonId) || null;
} 