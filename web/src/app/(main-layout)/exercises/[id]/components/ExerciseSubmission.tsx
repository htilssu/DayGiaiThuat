"use client";

import { useState, useEffect } from "react";
import {
  IconCircleCheck,
  IconCircleX,
  IconPlayerPlay,
} from "@tabler/icons-react";
import { ExerciseDetail, TestResult } from "./types";
import AIChat from "./AIChat";
import { runTests, testCases } from "@/services/codeRunner";
import MonacoEditor from "@/components/ui/MonacoEditor";

/**
 * Component cho phần nộp bài tập và chạy test
 *
 * @param {Object} props - Props của component
 * @param {ExerciseDetail} props.exercise - Thông tin chi tiết bài tập
 * @param {() => void} props.onSubmit - Hàm xử lý khi nộp bài
 * @returns {JSX.Element} Form nộp bài
 */
export default function ExerciseSubmission({
  exercise,
  onSubmit,
}: {
  exercise: ExerciseDetail;
  onSubmit: () => void;
}) {
  const [testResults /*setTestResults*/] = useState<TestResult[]>([]);
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [allTestsPassed /*setAllTestsPassed*/] = useState(false);
  const [callAIChat, setCallAIChat] = useState(false);
  const calling = {
    callAIChat,
    setCallAIChat,
  };

  const [code, setCode] = useState(`function yourFunction() {
  // Write your code here
  return;
}`);
  const [language, setLanguage] = useState("javascript");
  const [results, setResults] = useState<
    Array<{
      input: string;
      expectedOutput: string;
      actualOutput: string;
      passed: boolean;
      error: string;
    }>
  >([]);

  // Giả lập chạy test
  const handleRunTests = () => {
    setIsRunningTests(true);
    // setTestResults([]);

    // Mô phỏng việc chạy test bằng cách tạo kết quả ngẫu nhiên
    // setTimeout(() => {
    //   const results: TestResult[] = exercise.testCases.map(
    //     (testCase, index) => {
    //       // Giả lập kết quả test, trong thực tế sẽ chạy code thật với test case
    //       // 70% khả năng test pass cho mô phỏng
    //       const passed = Math.random() > 0.3;
    //       return {
    //         passed,
    //         input: testCase.input,
    //         expectedOutput: testCase.expectedOutput,
    //         actualOutput: passed
    //           ? testCase.expectedOutput
    //           : `Kết quả sai: ${index + Math.floor(Math.random() * 100)}`,
    //         error: passed
    //           ? undefined
    //           : Math.random() > 0.5
    //           ? "Runtime error: Lỗi chia cho 0"
    //           : undefined,
    //       };
    //     }
    //   );

    //   setTestResults(results);
    //   setAllTestsPassed(results.every((result) => result.passed));
    //   setIsRunningTests(false);
    // }, 1500);
    setTimeout(() => {
      const testResults = runTests(code, testCases);
      setResults(testResults);

      setIsRunningTests(false);
    }, 1500);
    console.log("callAIChat", results);
    console.log("content", exercise);
    setCallAIChat(true);
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

  // const editorRef = useRef<HTMLTextAreaElement | null>(null);
  // const lineNumbersRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Remove displayLineNumbers call
  }, [code]);

  return (
    <div className="space-y-6">
      {/* Editor and Chat */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Code editor with Run Test button */}
        <div className="space-y-4">
          <div className="border border-foreground/10 rounded-lg theme-transition">
            <div className="bg-foreground/5 p-3 border-b border-foreground/10 flex justify-between items-center">
              <h3 className="font-medium text-foreground px-5">Code</h3>
              <div className="relative">
                <select
                  id="language"
                  aria-label="Chọn ngôn ngữ lập trình"
                  className="w-full bg-transparent placeholder:text-primary text-primary text-sm border border-primary rounded-xl pl-4 pr-8 py-2 transition duration-300 ease focus:outline-none focus:border-primary hover:border-primary shadow-sm focus:shadow appearance-none cursor-pointer"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}>
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="csharp">C#</option>
                  <option value="c">C</option>
                  <option value="cpp">C++</option>
                  <option value="java">Java</option>
                  <option value="php">PHP</option>
                  <option value="ruby">Ruby</option>
                  <option value="swift">Swift</option>
                </select>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke-width="1.2"
                  stroke="currentColor"
                  className="h-5 w-5 ml-1 absolute top-2.5 right-2.5 text-primary">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M8.25 15 12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9"
                  />
                </svg>
              </div>
            </div>

            <div className="flex relative h-96">
              <MonacoEditor
                value={code}
                language={language}
                theme="vs"
                onChange={setCode}
                height={"100%"}
              />
            </div>
          </div>

          <button
            onClick={handleRunTests}
            disabled={isRunningTests}
            className={`w-full flex items-center justify-center gap-2 px-4 py-3 bg-primary/10 hover:bg-primary/20 text-primary font-medium rounded-lg transition-colors ${
              isRunningTests ? "opacity-60 cursor-not-allowed" : ""
            }`}>
            {isRunningTests ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary"></div>
                <span>Đang chạy...</span>
              </>
            ) : (
              <>
                <IconPlayerPlay className="h-5 w-5" />
                <span>Chạy Test</span>
              </>
            )}
          </button>
        </div>

        {/* AI Chat */}
        <div className="h-full">
          <AIChat
            code={code}
            results={results}
            calling={calling}
            title={exercise.title}
          />
        </div>
      </div>

      {/* Test results with Submit button */}
      <div className="space-y-4">
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
              }`}>
              {results.length === 0
                ? "Chưa chạy test"
                : allTestsPassed
                ? "Tất cả test đã pass!"
                : `${results.filter((r) => r.passed).length}/${
                    results.length
                  } test passed`}
            </div>
          </div>

          <div className="p-4 max-h-96 overflow-y-auto">
            {isRunningTests ? (
              <div className="flex items-center justify-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                <span className="ml-3 text-foreground/60">
                  Đang chạy test...
                </span>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center text-foreground/60 h-32 flex items-center justify-center">
                <div>
                  <IconPlayerPlay className="mx-auto h-12 w-12 text-foreground/30" />
                  <p className="mt-2">
                    Nhấn nút &quot;Chạy Test&quot; để kiểm tra code của bạn
                  </p>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div
                    key={index}
                    className={`border rounded-lg p-3 ${
                      result.passed
                        ? "border-green-200 bg-green-50 dark:bg-green-900/10 dark:border-green-900/30"
                        : "border-red-200 bg-red-50 dark:bg-red-900/10 dark:border-red-900/30"
                    } theme-transition`}>
                    <div className="flex justify-between items-center mb-2">
                      <div className="font-medium text-sm">
                        Test Case #{index + 1}
                      </div>
                      <div
                        className={`text-xs font-medium ${
                          result.passed
                            ? "text-green-600 dark:text-green-400"
                            : "text-red-600 dark:text-red-400"
                        }`}>
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
                          }`}>
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

        {/* Submit button */}
        {testResults.length > 0 && (
          <div className="flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={isRunningTests || !allTestsPassed}
              className={`px-6 py-3 bg-primary text-white font-medium rounded-lg transition-colors ${
                isRunningTests || !allTestsPassed
                  ? "opacity-60 cursor-not-allowed"
                  : "hover:bg-primary/90"
              }`}>
              {allTestsPassed
                ? "Nộp bài"
                : "Vui lòng pass tất cả test để nộp bài"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
