"use client";

import { useState, useEffect } from "react";
import {
  IconCircleCheck,
  IconCircleX,
  IconPlayerPlay,
} from "@tabler/icons-react";
import { ExerciseDetail, TestResult } from "./types";
import AIChat from "./AIChat";
import MonacoEditor from "@/components/ui/MonacoEditor";
import { exercisesApi } from "@/lib/api";
import { wrapUserCode } from "@/lib/utils/codeWrapper";
import { sendAIChatRequest } from "@/lib/api/aiChat";

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
  const [isRunningTests] = useState(false);
  const [callAIChat, setCallAIChat] = useState(false);

  const initialCode = [
    {
      language: "javascript",
      code: `function yourFunction(input) {
  // Write your code here. The system will automatically pass params from test cases.
  return input;
}`,
    },
    {
      language: "python",
      code: `def your_function(input):
    # Write your code here. The system will automatically pass params from test cases.
    return input`,
    },
    {
      language: "typescript",
      code: `function yourFunction(input: unknown) {
  // Write your code here. The system will automatically pass params from test cases.
  return input as unknown;
}`,
    },
    {
      language: "c",
      code: `#include <stdio.h>

int main() {
    // Write your code here
    return 0;
}`,
    },
    {
      language: "cpp",
      code: `#include <iostream>
using namespace std;

int main() {
    // Write your code here
    return 0;
}`,
    },
    {
      language: "java",
      code: `public class Main {
    public static void main(String[] args) {
        // Write your code here
    }
}`,
    },
    {
      language: "csharp",
      code: `using System;

class Program {
    static void Main(string[] args) {
        // Write your code here
    }
}`,
    },
    {
      language: "php",
      code: `<?php
// Write your code here
?>`,
    },
    {
      language: "ruby",
      code: `def your_function
  # Write your code here
end

your_function`,
    },
    {
      language: "swift",
      code: `func yourFunction() {
    // Write your code here
}

yourFunction()`,
    },
  ];

  const [code, setCode] = useState(initialCode[0].code);
  const [language, setLanguage] = useState("javascript");
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<
    Array<{
      input: string;
      expectedOutput: string;
      actualOutput: string;
      passed: boolean;
      error: string;
    }>
  >([]);
  const [isRunningJudge0, setIsRunningJudge0] = useState(false);
  const [aiResponse, setAiResponse] = useState<string>("");
  const [allTestsPassed, setAllTestsPassed] = useState(false);

  const calling = {
    callAIChat,
    setCallAIChat,
    allTestsPassed,
  };

  // Test Judge0 functionality
  const handleTestJudge0 = async () => {
    setIsRunningJudge0(true);
    setIsLoading(true);
    try {
      // Call backend API for Judge0 submission
      const wrapped = wrapUserCode(code, language);
      const response = await exercisesApi.sendCodeToJudge(Number(exercise.id), {
        code: wrapped,
        language,
      });
      // Ensure error is always a string
      setResults(
        response.results.map((r) => ({
          ...r,
          error: r.error ?? "",
        }))
      );

      // Gọi API ai-chat với kết quả test mới
      const testsPassed = response.results.every((result) => result.passed);
      setAllTestsPassed(testsPassed);
      try {
        const aiRes = await sendAIChatRequest({
          code,
          results: response.results,
          title: exercise.title,
          allTestsPassed: testsPassed,
        });
        if (aiRes.reply) {
          setAiResponse(aiRes.reply);
        }
      } catch (aiError) {
        console.error("AI Chat error:", aiError);
      }
      console.log("result", response.results);
      console.log("allTestsPassed", testsPassed);
    } catch (err) {
      console.error("Judge0 error:", err);
      alert("Error sending code to Judge0: " + err);
      setResults([]);
    } finally {
      setCallAIChat(true);
      setIsRunningJudge0(false);
      setIsLoading(false);
    }
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

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedLang = e.target.value;
    setLanguage(selectedLang);
    const found = initialCode.find((item) => item.language === selectedLang);
    if (found) setCode(found.code);
  };

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
                  onChange={handleLanguageChange}>
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
                  strokeWidth="1.2"
                  stroke="currentColor"
                  className="h-5 w-5 ml-1 absolute top-2.5 right-2.5 text-primary">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M8.25 15 12 18.75 15.75 15m-7.5-6L12 5.25 15.75 9"
                  />
                </svg>
              </div>
            </div>

            <div className="flex relative h-96 overflow-hidden rounded-b-lg">
              <MonacoEditor
                value={code}
                language={language}
                theme="vs"
                onChange={setCode}
                height={"100%"}
              />
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleTestJudge0}
              disabled={isRunningTests}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-primary/10 hover:bg-primary/20 text-primary font-medium rounded-lg transition-colors ${
                isRunningJudge0 ? "opacity-60 cursor-not-allowed" : ""
              }`}>
              {isRunningJudge0 ? (
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

            {/* <button
              onClick={handleTestJudge0}
              disabled={isRunningJudge0}
              className={`flex items-center justify-center gap-2 px-4 py-3 bg-blue-500/10 hover:bg-blue-500/20 text-blue-500 font-medium rounded-lg transition-colors ${
                isRunningJudge0 ? "opacity-60 cursor-not-allowed" : ""
              }`}>
              {isRunningJudge0 ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
                  <span>Judge0...</span>
                </>
              ) : (
                <>
                  <IconCode className="h-5 w-5" />
                  <span>Judge0</span>
                </>
              )}
            </button> */}
          </div>
        </div>

        <div className="border border-foreground/10 rounded-lg overflow-hidden theme-transition">
          <div className="bg-foreground/5 p-3 border-b border-foreground/10 flex justify-between items-center">
            <h3 className="font-medium text-foreground px-5">Kết quả test</h3>
            <div
              className={`flex items-center justify-center text-xs border border-primary rounded-xl px-3 py-3 shadow-sm ${
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
      </div>

      {/* Test results with Submit button */}
      <div className="space-y-4">
        {/* AI Chat */}
        <div className="h-full">
          <AIChat
            code={code}
            results={results}
            calling={calling}
            title={exercise.title}
            aiResponse={aiResponse}
            isLoading={isLoading}
            setIsLoading={setIsLoading}
          />
        </div>

        {/* Submit button */}
        {results.length > 0 && (
          <div className="flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={isRunningTests || !allTestsPassed}
              className={`px-6 py-3 w-full bg-primary text-white font-bold text-xl rounded-lg transition-colors ${
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
