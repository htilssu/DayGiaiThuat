export interface ExerciseItem {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  estimatedTime: string;
  completionRate: number;
  completed: boolean;
  content: string;
  codeTemplate: string;
  testCases: { input: string; expectedOutput: string }[];
}

export const exercisesData: ExerciseItem[] = [
  {
    id: 1,
    title: "Tìm kiếm nhị phân",
    description:
      "Cài đặt thuật toán tìm kiếm nhị phân và phân tích độ phức tạp",
    category: "Tìm kiếm",
    difficulty: "Beginner",
    estimatedTime: "30 phút",
    completionRate: 78,
    completed: true,
    content: `# Tìm kiếm nhị phân

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
      { input: "[1, 3, 5, 7, 9, 11, 13, 15], 7", expectedOutput: "3" },
      { input: "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1", expectedOutput: "0" },
      { input: "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 10", expectedOutput: "9" },
      { input: "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 11", expectedOutput: "-1" },
    ],
  },
  {
    id: 2,
    title: "Sắp xếp nhanh (Quick Sort)",
    description: "Cài đặt thuật toán sắp xếp nhanh với phân hoạch Lomuto",
    category: "Sắp xếp",
    difficulty: "Intermediate",
    estimatedTime: "45 phút",
    completionRate: 65,
    completed: false,
    content: `# Sắp xếp nhanh (Quick Sort)

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
        expectedOutput: "[2,3,5,6,7,9,10,11,12,14]",
      },
      { input: "[5, 4, 3, 2, 1]", expectedOutput: "[1,2,3,4,5]" },
      { input: "[1, 1, 1, 1, 1]", expectedOutput: "[1,1,1,1,1]" },
      {
        input: "[3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]",
        expectedOutput: "[1,1,2,3,3,4,5,5,5,6,9]",
      },
    ],
  },
  {
    id: 3,
    title: "Cây nhị phân tìm kiếm",
    description:
      "Cài đặt cấu trúc dữ liệu cây nhị phân tìm kiếm với các thao tác cơ bản",
    category: "Cấu trúc dữ liệu",
    difficulty: "Intermediate",
    estimatedTime: "60 phút",
    completionRate: 52,
    completed: false,
    content: `# Cây nhị phân tìm kiếm

Viết các hàm cơ bản cho cây nhị phân tìm kiếm (BST): thêm, tìm kiếm, xóa.
`,
    codeTemplate: `class Node:
    def __init__(self, key):
        self.left = None
        self.right = None
        self.val = key

# Viết các hàm insert, search, delete tại đây
`,
    testCases: [
      {
        input: "insert: [5, 3, 7, 2, 4, 6, 8]; search: 4",
        expectedOutput: "True",
      },
      {
        input: "insert: [5, 3, 7, 2, 4, 6, 8]; search: 10",
        expectedOutput: "False",
      },
    ],
  },
  {
    id: 4,
    title: "Thuật toán Dijkstra",
    description: "Tìm đường đi ngắn nhất trên đồ thị có trọng số không âm",
    category: "Đồ thị",
    difficulty: "Advanced",
    estimatedTime: "90 phút",
    completionRate: 42,
    completed: false,
    content: `# Thuật toán Dijkstra

Cài đặt thuật toán Dijkstra để tìm đường đi ngắn nhất từ một đỉnh đến các đỉnh còn lại trong đồ thị có trọng số không âm.
`,
    codeTemplate: `def dijkstra(graph, start):
    # graph: dict, start: int
    # Triển khai thuật toán tại đây
    pass
`,
    testCases: [
      {
        input: "graph: {0: [(1, 2), (2, 4)], 1: [(2, 1)], 2: []}, start: 0",
        expectedOutput: "{0: 0, 1: 2, 2: 3}",
      },
    ],
  },
  {
    id: 5,
    title: "Quy hoạch động - Dãy con tăng dài nhất",
    description:
      "Giải quyết bài toán tìm dãy con tăng dài nhất bằng quy hoạch động",
    category: "Quy hoạch động",
    difficulty: "Advanced",
    estimatedTime: "75 phút",
    completionRate: 38,
    completed: false,
    content: `# Dãy con tăng dài nhất

Tìm độ dài dãy con tăng dài nhất trong một dãy số nguyên.
`,
    codeTemplate: `def length_of_lis(nums):
    # Triển khai thuật toán tại đây
    pass
`,
    testCases: [
      { input: "[10,9,2,5,3,7,101,18]", expectedOutput: "4" },
      { input: "[0,1,0,3,2,3]", expectedOutput: "4" },
    ],
  },
  {
    id: 6,
    title: "Số Fibonacci",
    description:
      "Cài đặt các phương pháp tính số Fibonacci và so sánh hiệu suất",
    category: "Đệ quy",
    difficulty: "Beginner",
    estimatedTime: "30 phút",
    completionRate: 85,
    completed: true,
    content: `# Số Fibonacci

Viết hàm tính số Fibonacci thứ n bằng cả phương pháp đệ quy và quy hoạch động.
`,
    codeTemplate: `def fibonacci(n):
    # Triển khai thuật toán tại đây
    pass
`,
    testCases: [
      { input: "5", expectedOutput: "5" },
      { input: "10", expectedOutput: "55" },
    ],
  },
];
