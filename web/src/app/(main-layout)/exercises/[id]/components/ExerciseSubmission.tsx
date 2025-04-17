"use client";

import { useState } from "react";
import {
  IconCircleCheck,
  IconCircleX,
  IconPlayerPlay,
  IconCircle,
} from "@tabler/icons-react";
import { ExerciseDetail, TestResult } from "./types";

/**
 * Component cho phần nộp bài tập và chạy test
 *
 * @param {Object} props - Props của component
 * @param {ExerciseDetail} props.exercise - Thông tin chi tiết bài tập
 * @param {string} props.userCode - Code của người dùng
 * @param {(code: string) => void} props.setUserCode - Hàm cập nhật code
 * @param {() => void} props.onSubmit - Hàm xử lý khi nộp bài
 * @returns {JSX.Element} Form nộp bài
 */
export default function ExerciseSubmission({
  exercise,
  userCode,
  setUserCode,
  onSubmit,
}: {
  exercise: ExerciseDetail;
  userCode: string;
  setUserCode: (code: string) => void;
  onSubmit: () => void;
}) {
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [allTestsPassed, setAllTestsPassed] = useState(false);

  // Giả lập chạy test
  const runTests = () => {
    setIsRunningTests(true);
    setTestResults([]);

    // Mô phỏng việc chạy test bằng cách tạo kết quả ngẫu nhiên
    setTimeout(() => {
      const results: TestResult[] = exercise.testCases.map(
        (testCase, index) => {
          // Giả lập kết quả test, trong thực tế sẽ chạy code thật với test case
          // 70% khả năng test pass cho mô phỏng
          const passed = Math.random() > 0.3;
          return {
            passed,
            input: testCase.input,
            expectedOutput: testCase.expectedOutput,
            actualOutput: passed
              ? testCase.expectedOutput
              : `Kết quả sai: ${index + Math.floor(Math.random() * 100)}`,
            error: passed
              ? undefined
              : Math.random() > 0.5
              ? "Runtime error: Lỗi chia cho 0"
              : undefined,
          };
        }
      );

      setTestResults(results);
      setAllTestsPassed(results.every((result) => result.passed));
      setIsRunningTests(false);
    }, 1500);
  };

  // Xử lý nộp bài
  const handleSubmit = () => {
    if (allTestsPassed) {
      onSubmit();
    } else {
      // Thông báo lỗi nếu các test chưa pass
      alert(
        "Vui lòng chạy test và đảm bảo tất cả test case đều pass trước khi nộp bài!"
      );
    }
  };

  return (
    <div className="space-y-6">
      {/* Editor và kết quả test */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Code editor */}
        <div className="border border-foreground/10 rounded-lg overflow-hidden theme-transition">
          <div className="bg-foreground/5 p-3 border-b border-foreground/10 flex justify-between items-center">
            <h3 className="font-medium text-foreground">Mã nguồn</h3>
            <div className="text-xs text-foreground/60">Python</div>
          </div>

          <textarea
            value={userCode}
            onChange={(e) => setUserCode(e.target.value)}
            className="w-full h-96 p-4 bg-background text-foreground/90 font-mono text-sm resize-none focus:outline-none theme-transition"
            placeholder="Viết code của bạn ở đây..."
          ></textarea>
        </div>

        {/* Test results */}
        <div className="border border-foreground/10 rounded-lg overflow-hidden theme-transition">
          <div className="bg-foreground/5 p-3 border-b border-foreground/10 flex justify-between items-center">
            <h3 className="font-medium text-foreground">Kết quả test</h3>
            <div
              className={`text-xs ${
                allTestsPassed
                  ? "text-green-500"
                  : testResults.length > 0
                  ? "text-red-500"
                  : "text-foreground/60"
              }`}
            >
              {testResults.length === 0
                ? "Chưa chạy test"
                : allTestsPassed
                ? "Tất cả test đã pass!"
                : `${testResults.filter((r) => r.passed).length}/${
                    testResults.length
                  } test passed`}
            </div>
          </div>

          <div className="p-4 h-96 overflow-y-auto">
            {isRunningTests ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <span className="ml-3 text-foreground/60">
                  Đang chạy test...
                </span>
              </div>
            ) : testResults.length === 0 ? (
              <div className="text-center text-foreground/60 h-full flex items-center justify-center">
                <div>
                  <IconPlayerPlay className="mx-auto h-12 w-12 text-foreground/30" />
                  <p className="mt-2">
                    Nhấn nút "Chạy Test" để kiểm tra code của bạn
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {testResults.map((result, index) => (
                  <div
                    key={index}
                    className={`border rounded-lg p-3 ${
                      result.passed
                        ? "border-green-200 bg-green-50 dark:bg-green-900/10 dark:border-green-900/30"
                        : "border-red-200 bg-red-50 dark:bg-red-900/10 dark:border-red-900/30"
                    } theme-transition`}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <div className="font-medium text-sm">
                        Test Case #{index + 1}
                      </div>
                      <div
                        className={`text-xs font-medium ${
                          result.passed
                            ? "text-green-600 dark:text-green-400"
                            : "text-red-600 dark:text-red-400"
                        }`}
                      >
                        {result.passed ? (
                          <span className="flex items-center">
                            <IconCircleCheck className="h-4 w-4 mr-1" />
                            Pass
                          </span>
                        ) : (
                          <span className="flex items-center">
                            <IconCircleX className="h-4 w-4 mr-1" />
                            Fail
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="text-xs space-y-1">
                      <div>
                        <span className="font-medium text-foreground/70">
                          Input:
                        </span>
                        <span className="ml-2 text-foreground/80 font-mono">
                          {result.input}
                        </span>
                      </div>

                      <div>
                        <span className="font-medium text-foreground/70">
                          Expected:
                        </span>
                        <span className="ml-2 text-foreground/80 font-mono">
                          {result.expectedOutput}
                        </span>
                      </div>

                      <div>
                        <span className="font-medium text-foreground/70">
                          Actual:
                        </span>
                        <span
                          className={`ml-2 font-mono ${
                            result.passed
                              ? "text-foreground/80"
                              : "text-red-600 dark:text-red-400"
                          }`}
                        >
                          {result.actualOutput}
                        </span>
                      </div>

                      {result.error && (
                        <div className="mt-1 text-red-600 dark:text-red-400 font-mono">
                          {result.error}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Buttons */}
      <div className="flex justify-between">
        <button
          onClick={runTests}
          disabled={isRunningTests}
          className={`px-4 py-2 bg-foreground/10 hover:bg-foreground/20 text-foreground rounded-md transition-colors ${
            isRunningTests ? "opacity-60 cursor-not-allowed" : ""
          }`}
        >
          {isRunningTests ? "Đang chạy..." : "Chạy Test"}
        </button>

        <button
          onClick={handleSubmit}
          disabled={isRunningTests || !allTestsPassed}
          className={`px-4 py-2 bg-primary text-white rounded-md transition-colors ${
            isRunningTests || !allTestsPassed
              ? "opacity-60 cursor-not-allowed"
              : "hover:bg-primary/90"
          }`}
        >
          Nộp bài
        </button>
      </div>

      {/* Thông báo */}
      {allTestsPassed && (
        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg dark:bg-green-900/20 dark:border-green-900/30 dark:text-green-400 theme-transition">
          <div className="flex">
            <div className="flex-shrink-0">
              <IconCircleCheck className="h-5 w-5 text-green-500" />
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium">
                Tất cả test case đã pass! Bạn có thể nộp bài ngay bây giờ.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
