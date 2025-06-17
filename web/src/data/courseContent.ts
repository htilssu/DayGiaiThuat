export interface Lesson {
  id: number;
  title: string;
  duration: number; // in minutes
  videoUrl?: string;
  description: string;
  type: "video" | "quiz" | "exercise";
  isPreview?: boolean;
}

export interface Chapter {
  id: number;
  title: string;
  description: string;
  lessons: Lesson[];
}

export const dsaCourseContent: Chapter[] = [
  {
    id: 1,
    title: "Giới thiệu về Cấu trúc dữ liệu và Giải thuật",
    description: "Tổng quan về CTDL&GT và tầm quan trọng trong lập trình",
    lessons: [
      {
        id: 1,
        title: "Cấu trúc dữ liệu và Giải thuật là gì?",
        duration: 15,
        description:
          "Giới thiệu tổng quan về CTDL&GT và vai trò của chúng trong lập trình",
        type: "exercise",
        isPreview: true,
      },
      {
        id: 2,
        title: "Tại sao cần học CTDL&GT?",
        duration: 20,
        description:
          "Hiểu về tầm quan trọng và ứng dụng của CTDL&GT trong thực tế",
        type: "video",
        isPreview: true,
      },
      {
        id: 3,
        title: "Quiz: Kiến thức cơ bản",
        duration: 15,
        description: "Kiểm tra kiến thức về các khái niệm cơ bản",
        type: "quiz",
        isPreview: true,
      },
    ],
  },
  {
    id: 2,
    title: "Mảng và Danh sách liên kết",
    description:
      "Tìm hiểu về hai cấu trúc dữ liệu cơ bản: Mảng và Danh sách liên kết",
    lessons: [
      {
        id: 4,
        title: "Mảng một chiều và đa chiều",
        duration: 25,
        description: "Học về cách tổ chức và thao tác với mảng",
        type: "video",
        isPreview: true,
      },
      {
        id: 5,
        title: "Danh sách liên kết đơn",
        duration: 30,
        description:
          "Tìm hiểu về cấu trúc và các thao tác cơ bản với danh sách liên kết đơn",
        type: "video",
        isPreview: true,
      },
      {
        id: 6,
        title: "Bài tập: Thao tác với mảng",
        duration: 45,
        description: "Thực hành các thao tác cơ bản với mảng",
        type: "exercise",
        isPreview: true,
      },
    ],
  },
  {
    id: 3,
    title: "Ngăn xếp và Hàng đợi",
    description: "Khám phá hai cấu trúc dữ liệu quan trọng: Stack và Queue",
    lessons: [
      {
        id: 7,
        title: "Ngăn xếp (Stack)",
        duration: 25,
        description: "Hiểu về cấu trúc LIFO và các thao tác với Stack",
        type: "video",
        isPreview: true,
      },
      {
        id: 8,
        title: "Hàng đợi (Queue)",
        duration: 25,
        description: "Tìm hiểu về cấu trúc FIFO và các thao tác với Queue",
        type: "video",
        isPreview: true,
      },
      {
        id: 9,
        title: "Bài tập: Ứng dụng Stack và Queue",
        duration: 40,
        description: "Thực hành giải quyết các bài toán sử dụng Stack và Queue",
        type: "exercise",
        isPreview: true,
      },
    ],
  },
  {
    id: 4,
    title: "Cây nhị phân và Cây tìm kiếm nhị phân",
    description: "Tìm hiểu về cấu trúc cây và các thuật toán liên quan",
    lessons: [
      {
        id: 10,
        title: "Cây nhị phân cơ bản",
        duration: 30,
        description: "Học về cấu trúc và các khái niệm cơ bản của cây nhị phân",
        type: "video",
        isPreview: true,
      },
      {
        id: 11,
        title: "Cây tìm kiếm nhị phân (BST)",
        duration: 35,
        description: "Tìm hiểu về BST và các thao tác cơ bản",
        type: "video",
        isPreview: true,
      },
      {
        id: 12,
        title: "Quiz: Cây nhị phân",
        duration: 20,
        description: "Kiểm tra kiến thức về cây nhị phân và BST",
        type: "quiz",
        isPreview: true,
      },
    ],
  },
  {
    id: 5,
    title: "Thuật toán sắp xếp cơ bản",
    description:
      "Học về các thuật toán sắp xếp phổ biến và hiệu suất của chúng",
    lessons: [
      {
        id: 13,
        title: "Bubble Sort và Selection Sort",
        duration: 30,
        description: "Tìm hiểu về hai thuật toán sắp xếp đơn giản",
        type: "video",
        isPreview: true,
      },
      {
        id: 14,
        title: "Insertion Sort và Quick Sort",
        duration: 35,
        description: "Học về hai thuật toán sắp xếp hiệu quả hơn",
        type: "video",
        isPreview: true,
      },
      {
        id: 15,
        title: "Bài tập: Implement thuật toán sắp xếp",
        duration: 50,
        description: "Thực hành cài đặt các thuật toán sắp xếp đã học",
        type: "exercise",
        isPreview: true,
      },
    ],
  },
];
