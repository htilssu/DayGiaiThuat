interface TestCase {
  input: string;
  expectedOutput: string;
}

interface TestResult {
  input: string;
  expectedOutput: string;
  actualOutput: string;
  passed: boolean;
  error: string;
}

export function runTests(code: string, testCases: TestCase[]): TestResult[] {
  try {
    // Tạo một hàm từ code được nhập vào
    const fn = new Function(
      "arr",
      `
      ${code}
      return sumArray(arr);
    `
    );

    return testCases.map((testCase) => {
      try {
        // Parse input từ string sang array
        const input = JSON.parse(testCase.input);
        const expected = testCase.expectedOutput;

        // Thực thi hàm với input
        const actual = fn(input);

        // So sánh kết quả
        const passed = actual.toString() === expected;

        return {
          input: testCase.input,
          expectedOutput: expected,
          actualOutput: actual.toString(),
          passed,
          error: "",
        };
      } catch (error) {
        return {
          input: testCase.input,
          expectedOutput: testCase.expectedOutput,
          actualOutput: `Error: ${error.message}`,
          passed: false,
          error: `Error: ${error.message}`,
        };
      }
    });
  } catch (error) {
    return [
      {
        input: "N/A",
        expectedOutput: "N/A",
        actualOutput: `Error: ${error.message}`,
        passed: false,
        error: `Error: ${error.message}`,
      },
    ];
  }
}

export const testCases: TestCase[] = [
  {
    input: "[1, 2, 3, 4, 5]",
    expectedOutput: "15",
  },
  {
    input: "[-1, -2, 3]",
    expectedOutput: "0",
  },
  {
    input: "[]",
    expectedOutput: "0",
  },
  {
    input: "[10, -10, 20, -20]",
    expectedOutput: "0",
  },
  {
    input: "[100]",
    expectedOutput: "100",
  },
  {
    input: "[0, 0, 0, 0]",
    expectedOutput: "0",
  },
  {
    input: "[5, 5, 5, 5]",
    expectedOutput: "20",
  },
  {
    input: "[-5, -15, -10]",
    expectedOutput: "-30",
  },
  {
    input: "[1.5, 2.5, 3]",
    expectedOutput: "7",
  },
  {
    input: "[1000, 2000, 3000]",
    expectedOutput: "6000",
  },
];
