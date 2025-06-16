// Định nghĩa các kiểu dữ liệu
interface LessonSection {
    type: "text" | "code" | "image" | "quiz";
    content: string;
    options?: string[];
    answer?: number;
    explanation?: string;
}

interface Lesson {
    id: string;
    title: string;
    description: string;
    topicId: string;
    topicTitle: string;
    sections: LessonSection[];
    nextLessonId?: string;
    prevLessonId?: string;
}

interface TopicLessons {
    [lessonId: string]: Lesson;
}

interface LessonsData {
    [topicId: string]: TopicLessons;
}

// Dữ liệu mẫu cho các bài học
export const sampleLessons: LessonsData = {
    "algorithms-basics": {
        "1": {
            id: "1",
            title: "Giới thiệu về Giải thuật",
            description: "Tìm hiểu về giải thuật là gì và tại sao chúng quan trọng trong lập trình",
            topicId: "algorithms-basics",
            topicTitle: "Cơ bản về giải thuật",
            sections: [
                {
                    type: "text",
                    content: `
            <h2>Giải thuật là gì?</h2>
            <p>Giải thuật (Algorithm) là một tập hợp hữu hạn các bước được định nghĩa rõ ràng để giải quyết một vấn đề cụ thể. Trong khoa học máy tính, giải thuật là một quy trình từng bước để thực hiện một tác vụ hoặc giải quyết một vấn đề.</p>
            <p>Một giải thuật tốt cần có các đặc điểm sau:</p>
            <ul>
              <li><strong>Tính chính xác</strong>: Giải thuật phải đưa ra kết quả chính xác cho mọi đầu vào hợp lệ.</li>
              <li><strong>Tính xác định</strong>: Mỗi bước của giải thuật phải được xác định rõ ràng, không có sự mơ hồ.</li>
              <li><strong>Tính hữu hạn</strong>: Giải thuật phải kết thúc sau một số bước hữu hạn.</li>
              <li><strong>Tính hiệu quả</strong>: Giải thuật nên sử dụng tài nguyên (thời gian, bộ nhớ) một cách hiệu quả.</li>
            </ul>
          `
                },
                {
                    type: "image",
                    content: "https://www.simplilearn.com/ice9/free_resources_article_thumb/Algorithms_Explained.jpg"
                },
                {
                    type: "text",
                    content: `
            <h2>Tại sao giải thuật quan trọng?</h2>
            <p>Giải thuật đóng vai trò quan trọng trong lập trình và khoa học máy tính vì những lý do sau:</p>
            <ul>
              <li>Giúp giải quyết các vấn đề phức tạp một cách hiệu quả</li>
              <li>Tối ưu hóa việc sử dụng tài nguyên (thời gian xử lý, bộ nhớ)</li>
              <li>Cung cấp cách tiếp cận có cấu trúc để giải quyết vấn đề</li>
              <li>Là nền tảng cho việc phát triển phần mềm chất lượng cao</li>
            </ul>
          `
                },
                {
                    type: "quiz",
                    content: "Đâu KHÔNG phải là đặc điểm của một giải thuật tốt?",
                    options: [
                        "Tính chính xác",
                        "Tính phức tạp cao",
                        "Tính xác định",
                        "Tính hữu hạn"
                    ],
                    answer: 1,
                    explanation: "Một giải thuật tốt nên có độ phức tạp thấp để sử dụng tài nguyên hiệu quả. Tính phức tạp cao thường không phải là đặc điểm mong muốn của một giải thuật tốt."
                }
            ],
            nextLessonId: "2"
        },
        "2": {
            id: "2",
            title: "Độ phức tạp của giải thuật",
            description: "Hiểu về cách đánh giá hiệu suất của giải thuật thông qua phân tích độ phức tạp",
            topicId: "algorithms-basics",
            topicTitle: "Cơ bản về giải thuật",
            sections: [
                {
                    type: "text",
                    content: `
            <h2>Độ phức tạp của giải thuật là gì?</h2>
            <p>Độ phức tạp của giải thuật là cách để đo lường hiệu suất của giải thuật dựa trên hai yếu tố chính:</p>
            <ul>
              <li><strong>Độ phức tạp thời gian</strong>: Lượng thời gian mà giải thuật cần để chạy.</li>
              <li><strong>Độ phức tạp không gian</strong>: Lượng bộ nhớ mà giải thuật cần để thực thi.</li>
            </ul>
            <p>Chúng ta thường sử dụng ký hiệu Big O để biểu thị độ phức tạp của giải thuật.</p>
          `
                },
                {
                    type: "code",
                    content: `// Ví dụ về giải thuật có độ phức tạp O(n)
function linearSearch(arr, target) {
  for (let i = 0; i < arr.length; i++) {
    if (arr[i] === target) {
      return i;
    }
  }
  return -1;
}

// Ví dụ về giải thuật có độ phức tạp O(n²)
function bubbleSort(arr) {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        // Hoán đổi phần tử
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
      }
    }
  }
  return arr;
}`
                },
                {
                    type: "text",
                    content: `
            <h2>Các loại độ phức tạp thời gian phổ biến</h2>
            <ul>
              <li><strong>O(1)</strong> - Độ phức tạp hằng số: Thời gian thực thi không phụ thuộc vào kích thước đầu vào.</li>
              <li><strong>O(log n)</strong> - Độ phức tạp logarit: Thời gian thực thi tăng theo logarit của kích thước đầu vào.</li>
              <li><strong>O(n)</strong> - Độ phức tạp tuyến tính: Thời gian thực thi tăng tuyến tính với kích thước đầu vào.</li>
              <li><strong>O(n log n)</strong> - Độ phức tạp tuyến tính logarit: Thường thấy trong các giải thuật sắp xếp hiệu quả.</li>
              <li><strong>O(n²)</strong> - Độ phức tạp bậc hai: Thời gian thực thi tăng theo bình phương của kích thước đầu vào.</li>
              <li><strong>O(2^n)</strong> - Độ phức tạp hàm mũ: Thời gian thực thi tăng theo hàm mũ của kích thước đầu vào.</li>
            </ul>
          `
                },
                {
                    type: "image",
                    content: "https://miro.medium.com/max/1400/1*5ZLci3SuR0zM_QlZOADv8Q.jpeg"
                },
                {
                    type: "quiz",
                    content: "Giải thuật tìm kiếm nhị phân (binary search) có độ phức tạp thời gian là gì?",
                    options: [
                        "O(1)",
                        "O(log n)",
                        "O(n)",
                        "O(n²)"
                    ],
                    answer: 1,
                    explanation: "Tìm kiếm nhị phân có độ phức tạp thời gian là O(log n) vì mỗi lần so sánh, nó loại bỏ một nửa phạm vi tìm kiếm."
                }
            ],
            prevLessonId: "1",
            nextLessonId: "3"
        }
    },
    "data-structures": {
        "1": {
            id: "1",
            title: "Giới thiệu về Cấu trúc dữ liệu",
            description: "Tìm hiểu về cấu trúc dữ liệu và vai trò của chúng trong lập trình",
            topicId: "data-structures",
            topicTitle: "Cấu trúc dữ liệu",
            sections: [
                {
                    type: "text",
                    content: `
            <h2>Cấu trúc dữ liệu là gì?</h2>
            <p>Cấu trúc dữ liệu là cách tổ chức và lưu trữ dữ liệu trong máy tính sao cho có thể truy cập và sửa đổi một cách hiệu quả. Cấu trúc dữ liệu đúng giúp tăng hiệu suất của giải thuật và tối ưu hóa việc sử dụng tài nguyên.</p>
            <p>Cấu trúc dữ liệu có thể được phân loại thành hai nhóm chính:</p>
            <ul>
              <li><strong>Cấu trúc dữ liệu nguyên thủy</strong>: Integer, Float, Boolean, Char</li>
              <li><strong>Cấu trúc dữ liệu không nguyên thủy</strong>: Array, List, Stack, Queue, Tree, Graph, etc.</li>
            </ul>
          `
                },
                {
                    type: "image",
                    content: "https://media.geeksforgeeks.org/wp-content/uploads/20220520182504/ClassificationofDataStructure-660x347.jpg"
                },
                {
                    type: "text",
                    content: `
            <h2>Tại sao cấu trúc dữ liệu quan trọng?</h2>
            <p>Cấu trúc dữ liệu đóng vai trò quan trọng trong lập trình vì:</p>
            <ul>
              <li>Giúp quản lý và tổ chức dữ liệu một cách hiệu quả</li>
              <li>Tối ưu hóa việc sử dụng bộ nhớ và thời gian xử lý</li>
              <li>Làm cho code dễ đọc, dễ bảo trì và mở rộng</li>
              <li>Cung cấp các phương thức tiêu chuẩn để thao tác với dữ liệu</li>
            </ul>
          `
                },
                {
                    type: "quiz",
                    content: "Đâu KHÔNG phải là cấu trúc dữ liệu không nguyên thủy?",
                    options: [
                        "Array (Mảng)",
                        "Integer (Số nguyên)",
                        "Tree (Cây)",
                        "Queue (Hàng đợi)"
                    ],
                    answer: 1,
                    explanation: "Integer (Số nguyên) là một cấu trúc dữ liệu nguyên thủy, không phải cấu trúc dữ liệu không nguyên thủy."
                }
            ],
            nextLessonId: "2"
        }
    }
};

// Hàm trợ giúp để lấy bài học theo topicId và lessonId
export function getLesson(topicId: string, lessonId: string): Lesson | null {
    if (sampleLessons[topicId] && sampleLessons[topicId][lessonId]) {
        return sampleLessons[topicId][lessonId];
    }
    return null;
} 