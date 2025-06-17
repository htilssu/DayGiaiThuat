"use client";

import { LearningRoadmap } from "./LearningRoadmap";

// Dữ liệu mẫu cho các topic
const sampleTopics = [
    {
        id: "algorithms-basics",
        title: "Cơ bản về giải thuật",
        description: "Tìm hiểu về các khái niệm cơ bản, độ phức tạp và cách phân tích giải thuật",
        color: "primary",
        status: "completed" as const,
        lessons: 5,
        completedLessons: 5,
        progress: 100
    },
    {
        id: "data-structures",
        title: "Cấu trúc dữ liệu",
        description: "Học về các cấu trúc dữ liệu phổ biến như mảng, danh sách liên kết, ngăn xếp, hàng đợi",
        color: "secondary",
        status: "active" as const,
        lessons: 8,
        completedLessons: 3,
        progress: 37.5
    },
    {
        id: "sorting-algorithms",
        title: "Giải thuật sắp xếp",
        description: "Tìm hiểu về các thuật toán sắp xếp như Bubble Sort, Quick Sort, Merge Sort và nhiều thuật toán khác",
        color: "accent",
        status: "active" as const,
        lessons: 6,
        completedLessons: 1,
        progress: 16.7
    },
    {
        id: "searching-algorithms",
        title: "Giải thuật tìm kiếm",
        description: "Khám phá các thuật toán tìm kiếm như tìm kiếm tuyến tính, tìm kiếm nhị phân và các biến thể",
        color: "primary",
        status: "locked" as const,
        lessons: 4,
        completedLessons: 0,
        progress: 0
    },
    {
        id: "graph-algorithms",
        title: "Giải thuật đồ thị",
        description: "Học về các thuật toán đồ thị như BFS, DFS, Dijkstra, và các thuật toán đường đi ngắn nhất",
        color: "secondary",
        status: "locked" as const,
        lessons: 7,
        completedLessons: 0,
        progress: 0
    },
    {
        id: "dynamic-programming",
        title: "Quy hoạch động",
        description: "Tìm hiểu về kỹ thuật quy hoạch động và cách áp dụng để giải quyết các bài toán phức tạp",
        color: "accent",
        status: "locked" as const,
        lessons: 10,
        completedLessons: 0,
        progress: 0
    }
];

export function LearnPage() {
    return <LearningRoadmap />;
} 