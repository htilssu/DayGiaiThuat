/**
 * Interface mô tả cấu trúc dữ liệu bài tập chi tiết
 * @interface ExerciseDetail
 * @property {number} id - ID duy nhất của bài tập
 * @property {string} title - Tiêu đề bài tập
 * @property {string} description - Mô tả ngắn gọn về bài tập
 * @property {string} category - Danh mục của bài tập
 * @property {string} difficulty - Độ khó (Dễ, Trung bình, Khó)
 * @property {string} estimatedTime - Thời gian ước tính để hoàn thành
 * @property {number} completionRate - Tỷ lệ hoàn thành bài tập (0-100)
 * @property {boolean} completed - Trạng thái hoàn thành của người dùng hiện tại
 * @property {string} content - Nội dung bài tập dạng Markdown
 * @property {string} codeTemplate - Mẫu code ban đầu
 * @property {TestCase[]} testCases - Danh sách các test case
 */
export interface ExerciseDetail {
  id: number;
  title: string;
  description: string;
  category: string;
  difficulty: "Dễ" | "Trung bình" | "Khó";
  estimatedTime: string;
  completionRate: number;
  completed: boolean;
  content: string;
  codeTemplate: string;
  testCases: TestCase[];
}

/**
 * Interface mô tả test case
 * @interface TestCase
 * @property {string} input - Dữ liệu đầu vào
 * @property {string} expectedOutput - Kết quả đầu ra mong đợi
 */
export interface TestCase {
  input: string;
  expectedOutput: string;
}

/**
 * Interface mô tả kết quả test
 * @interface TestResult
 * @property {boolean} passed - Kết quả đúng hoặc sai
 * @property {string} input - Dữ liệu đầu vào
 * @property {string} expectedOutput - Kết quả đầu ra mong đợi
 * @property {string} actualOutput - Kết quả đầu ra thực tế
 * @property {string} error - Thông báo lỗi (nếu có)
 */
export interface TestResult {
  passed: boolean;
  input: string;
  expectedOutput: string;
  actualOutput: string;
  error?: string;
}
