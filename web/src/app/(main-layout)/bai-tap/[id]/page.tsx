"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ExerciseDetail } from "./components/types";
import ExerciseSubmission from "./components/ExerciseSubmission";
import ExerciseHeader from "./components/ExerciseHeader";
import ExerciseContent from "./components/ExerciseContent";

/**
 * Dữ liệu mẫu chi tiết bài tập
 */
const exerciseData: Record<string, ExerciseDetail> = {
  "ex-001": {
    id: "ex-001",
    title: "Tìm kiếm nhị phân",
    description:
      "Cài đặt thuật toán tìm kiếm nhị phân và phân tích độ phức tạp",
    category: "Tìm kiếm",
    difficulty: "Dễ",
    estimatedTime: "30 phút",
    completionRate: 78,
    completed: true,
    content: `
# Tìm kiếm nhị phân

Tìm kiếm nhị phân là một thuật toán tìm kiếm hiệu quả cho mảng đã sắp xếp. Thuật toán này thực hiện theo nguyên tắc chia để trị, liên tục thu hẹp phạm vi tìm kiếm một nửa sau mỗi lần so sánh.

## Yêu cầu

Viết hàm tìm kiếm nhị phân thực hiện tìm kiếm một giá trị trong mảng đã sắp xếp. Hàm sẽ trả về vị trí của giá trị nếu tìm thấy, hoặc -1 nếu không tìm thấy.

### Đặc tả hàm

\`\`\`python
def binary_search(arr: list[int], target: int) -> int:
    """
    Tìm kiếm nhị phân trên mảng đã sắp xếp
    
    Args:
        arr: Mảng các số nguyên đã sắp xếp tăng dần
        target: Giá trị cần tìm kiếm
        
    Returns:
        Vị trí của target trong mảng nếu tìm thấy, -1 nếu không tìm thấy
    """
    # Triển khai thuật toán tại đây
    pass
\`\`\`

## Ví dụ

Đầu vào:
- arr = [1, 3, 5, 7, 9, 11, 13, 15]
- target = 7

Đầu ra:
- 3 (vì 7 nằm ở vị trí thứ 3 trong mảng, chỉ số bắt đầu từ 0)

## Phân tích

Thuật toán tìm kiếm nhị phân có độ phức tạp thời gian O(log n) do loại bỏ một nửa phạm vi tìm kiếm sau mỗi lần so sánh. Điều này làm cho nó hiệu quả hơn nhiều so với tìm kiếm tuyến tính (O(n)) đối với các tập dữ liệu lớn.

## Gợi ý

1. Khởi tạo hai biến left và right là chỉ số trái và phải của mảng.
2. Lặp lại cho đến khi left > right:
   - Tính chỉ số giữa mid = (left + right) // 2
   - Nếu arr[mid] == target, trả về mid
   - Nếu arr[mid] < target, cập nhật left = mid + 1
   - Nếu arr[mid] > target, cập nhật right = mid - 1
3. Trả về -1 nếu không tìm thấy target trong mảng.
    `,
    codeTemplate: `def binary_search(arr, target):
    """
    Tìm kiếm nhị phân trên mảng đã sắp xếp
    
    Args:
        arr: Mảng các số nguyên đã sắp xếp tăng dần
        target: Giá trị cần tìm kiếm
        
    Returns:
        Vị trí của target trong mảng nếu tìm thấy, -1 nếu không tìm thấy
    """
    # Triển khai thuật toán tại đây
    pass
    
# Test case
arr = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7
print(binary_search(arr, target))  # Kết quả mong đợi: 3`,
    testCases: [
      {
        input: "[1, 3, 5, 7, 9, 11, 13, 15], 7",
        expectedOutput: "3",
      },
      {
        input: "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1",
        expectedOutput: "0",
      },
      {
        input: "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10",
        expectedOutput: "9",
      },
      {
        input: "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 11",
        expectedOutput: "-1",
      },
    ],
  },
  "ex-002": {
    id: "ex-002",
    title: "Sắp xếp nhanh (Quick Sort)",
    description: "Cài đặt thuật toán sắp xếp nhanh với phân hoạch Lomuto",
    category: "Sắp xếp",
    difficulty: "Trung bình",
    estimatedTime: "45 phút",
    completionRate: 65,
    completed: false,
    content: `
# Sắp xếp nhanh (Quick Sort)

Quick Sort là một thuật toán sắp xếp hiệu quả dựa trên nguyên tắc chia để trị. Thuật toán chọn một phần tử làm "khóa" (pivot), phân hoạch mảng thành hai phần: những phần tử nhỏ hơn pivot và những phần tử lớn hơn pivot, sau đó đệ quy sắp xếp hai phần này.

## Yêu cầu

Viết hàm quick_sort thực hiện thuật toán sắp xếp nhanh với phân hoạch Lomuto. Hàm sẽ nhận vào một mảng các số nguyên và trả về mảng đã được sắp xếp tăng dần.

### Đặc tả hàm

\`\`\`python
def quick_sort(arr: list[int]) -> list[int]:
    """
    Sắp xếp mảng sử dụng thuật toán Quick Sort
    
    Args:
        arr: Mảng các số nguyên cần sắp xếp
        
    Returns:
        Mảng đã được sắp xếp
    """
    # Triển khai thuật toán tại đây
    pass
\`\`\`

## Ví dụ

Đầu vào:
- arr = [9, 7, 5, 11, 12, 2, 14, 3, 10, 6]

Đầu ra:
- [2, 3, 5, 6, 7, 9, 10, 11, 12, 14]

## Phân tích

Thuật toán Quick Sort có độ phức tạp thời gian trung bình là O(n log n), nhưng trong trường hợp xấu nhất có thể lên tới O(n²). Tuy nhiên, với cách chọn pivot hợp lý, trường hợp xấu nhất hiếm khi xảy ra trong thực tế.

## Gợi ý

1. Viết hàm phân hoạch Lomuto:
   - Chọn pivot là phần tử cuối cùng của mảng
   - Đặt chỉ số i để theo dõi vị trí phân hoạch
   - Duyệt qua mảng, di chuyển tất cả phần tử nhỏ hơn pivot về bên trái
   - Hoán đổi pivot vào vị trí cuối cùng của nhóm phần tử nhỏ hơn pivot
   - Trả về vị trí của pivot sau khi hoán đổi

2. Viết hàm quick_sort đệ quy:
   - Nếu mảng có ít hơn 2 phần tử, trả về mảng (điều kiện dừng)
   - Sử dụng hàm phân hoạch để nhận vị trí pivot
   - Gọi đệ quy quick_sort cho phần bên trái và bên phải của pivot
   - Kết hợp các phần đã sắp xếp lại với nhau
    `,
    codeTemplate: `def quick_sort(arr):
    """
    Sắp xếp mảng sử dụng thuật toán Quick Sort
    
    Args:
        arr: Mảng các số nguyên cần sắp xếp
        
    Returns:
        Mảng đã được sắp xếp
    """
    # Triển khai thuật toán tại đây
    pass
    
# Test case
arr = [9, 7, 5, 11, 12, 2, 14, 3, 10, 6]
print(quick_sort(arr))  # Kết quả mong đợi: [2, 3, 5, 6, 7, 9, 10, 11, 12, 14]`,
    testCases: [
      {
        input: "[9, 7, 5, 11, 12, 2, 14, 3, 10, 6]",
        expectedOutput: "[2, 3, 5, 6, 7, 9, 10, 11, 12, 14]",
      },
      {
        input: "[5, 4, 3, 2, 1]",
        expectedOutput: "[1, 2, 3, 4, 5]",
      },
      {
        input: "[1, 1, 1, 1, 1]",
        expectedOutput: "[1, 1, 1, 1, 1]",
      },
      {
        input: "[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]",
        expectedOutput: "[1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9]",
      },
    ],
  },
};

/**
 * Trang chi tiết bài tập
 *
 * @param {Object} props - Props của component
 * @param {Object} props.params - Tham số của trang
 * @param {string} props.params.id - ID của bài tập
 * @returns {JSX.Element} Trang chi tiết bài tập
 */
export default function ExerciseDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const [exercise, setExercise] = useState<ExerciseDetail | null>(null);
  const [userCode, setUserCode] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState<"description" | "submission">(
    "description"
  );

  // Tải dữ liệu bài tập khi component được render
  useEffect(() => {
    const loadExercise = () => {
      // Giả lập việc gọi API với dữ liệu giả
      setIsLoading(true);
      setTimeout(() => {
        const exercise = exerciseData[params.id];

        if (!exercise) {
          // Nếu không tìm thấy bài tập, chuyển hướng về trang danh sách
          router.push("/bai-tap");
          return;
        }

        setExercise(exercise);
        setUserCode(exercise.codeTemplate || "");
        setIsLoading(false);
      }, 500);
    };

    loadExercise();
  }, [params.id, router]);

  // Xử lý khi người dùng nộp bài
  const handleSubmit = () => {
    // Giả lập việc gửi code đi để chấm điểm
    setCurrentTab("submission");

    // Giả lập lưu tiến độ hoàn thành
    if (exercise) {
      setExercise({
        ...exercise,
        completed: true,
      });
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Nếu không tìm thấy bài tập
  if (!exercise) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-foreground mb-2">
          Không tìm thấy bài tập
        </h2>
        <p className="text-foreground/60 mb-4">
          Bài tập này không tồn tại hoặc đã bị xóa.
        </p>
        <Link
          href="/bai-tap"
          className="inline-flex items-center px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
        >
          Quay lại danh sách bài tập
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header bài tập */}
      <ExerciseHeader exercise={exercise} />

      {/* Tab điều hướng */}
      <div className="border-b border-foreground/10 mb-6">
        <div className="flex space-x-4">
          <button
            onClick={() => setCurrentTab("description")}
            className={`py-3 px-1 border-b-2 font-medium text-sm ${
              currentTab === "description"
                ? "border-primary text-primary"
                : "border-transparent text-foreground/70 hover:text-foreground hover:border-foreground/20"
            } transition-colors`}
          >
            Đề bài
          </button>
          <button
            onClick={() => setCurrentTab("submission")}
            className={`py-3 px-1 border-b-2 font-medium text-sm ${
              currentTab === "submission"
                ? "border-primary text-primary"
                : "border-transparent text-foreground/70 hover:text-foreground hover:border-foreground/20"
            } transition-colors`}
          >
            Nộp bài
          </button>
        </div>
      </div>

      {/* Nội dung bài tập */}
      {currentTab === "description" && (
        <ExerciseContent content={exercise.content} />
      )}

      {/* Phần nộp bài */}
      {currentTab === "submission" && (
        <ExerciseSubmission
          exercise={exercise}
          userCode={userCode}
          setUserCode={setUserCode}
          onSubmit={handleSubmit}
        />
      )}
    </div>
  );
}
