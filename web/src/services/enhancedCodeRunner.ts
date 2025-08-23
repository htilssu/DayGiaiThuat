/**
 * Enhanced test cases for the code runner
 * This extends the basic sumArray tests with more diverse test scenarios
 */

interface TestCase {
  input: string;
  expectedOutput: string;
  description?: string;
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
    // Create a function from the input code
    const fn = new Function(
      "arr",
      `
      ${code}
      return sumArray(arr);
    `
    );

    return testCases.map((testCase) => {
      try {
        // Parse input from string to array
        const input = JSON.parse(testCase.input);
        const expected = testCase.expectedOutput;

        // Execute function with input
        const actual = fn(input);

        // Compare results
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
          actualOutput: `Error: ${error instanceof Error ? error.message : String(error)}`,
          passed: false,
          error: `Error: ${error instanceof Error ? error.message : String(error)}`,
        };
      }
    });
  } catch (error) {
    return [
      {
        input: "N/A",
        expectedOutput: "N/A",
        actualOutput: `Error: ${error instanceof Error ? error.message : String(error)}`,
        passed: false,
        error: `Error: ${error instanceof Error ? error.message : String(error)}`,
      },
    ];
  }
}

// Enhanced test cases with better coverage
export const sumArrayTestCases: TestCase[] = [
  {
    input: "[1, 2, 3, 4, 5]",
    expectedOutput: "15",
    description: "Basic positive numbers"
  },
  {
    input: "[-1, -2, 3]",
    expectedOutput: "0",
    description: "Mixed positive and negative numbers"
  },
  {
    input: "[]",
    expectedOutput: "0",
    description: "Empty array"
  },
  {
    input: "[10, -10, 20, -20]",
    expectedOutput: "0",
    description: "Balanced positive and negative"
  },
  {
    input: "[100]",
    expectedOutput: "100",
    description: "Single element"
  },
  {
    input: "[0, 0, 0, 0]",
    expectedOutput: "0",
    description: "All zeros"
  },
  {
    input: "[5, 5, 5, 5]",
    expectedOutput: "20",
    description: "All same numbers"
  },
  {
    input: "[-5, -15, -10]",
    expectedOutput: "-30",
    description: "All negative numbers"
  },
  {
    input: "[1.5, 2.5, 3]",
    expectedOutput: "7",
    description: "Decimal numbers"
  },
  {
    input: "[1000, 2000, 3000]",
    expectedOutput: "6000",
    description: "Large numbers"
  }
];

// Test cases for different algorithms could be added here
export const fibonacciTestCases: TestCase[] = [
  {
    input: "0",
    expectedOutput: "0",
    description: "Fibonacci of 0"
  },
  {
    input: "1",
    expectedOutput: "1",
    description: "Fibonacci of 1"
  },
  {
    input: "5",
    expectedOutput: "5",
    description: "Fibonacci of 5"
  },
  {
    input: "10",
    expectedOutput: "55",
    description: "Fibonacci of 10"
  }
];

export const sortArrayTestCases: TestCase[] = [
  {
    input: "[3, 1, 4, 1, 5, 9]",
    expectedOutput: "[1,1,3,4,5,9]",
    description: "Basic sorting"
  },
  {
    input: "[]",
    expectedOutput: "[]",
    description: "Empty array"
  },
  {
    input: "[5]",
    expectedOutput: "[5]",
    description: "Single element"
  },
  {
    input: "[-3, -1, -4]",
    expectedOutput: "[-4,-3,-1]",
    description: "Negative numbers"
  }
];

// Function to run tests for different problem types
export function runTestsForProblem(
  code: string, 
  problemType: 'sumArray' | 'fibonacci' | 'sortArray',
  customTestCases?: TestCase[]
): TestResult[] {
  let testCases: TestCase[];
  let functionName: string;

  switch (problemType) {
    case 'sumArray':
      testCases = customTestCases || sumArrayTestCases;
      functionName = 'sumArray';
      break;
    case 'fibonacci':
      testCases = customTestCases || fibonacciTestCases;
      functionName = 'fibonacci';
      break;
    case 'sortArray':
      testCases = customTestCases || sortArrayTestCases;
      functionName = 'sortArray';
      break;
    default:
      throw new Error(`Unknown problem type: ${problemType}`);
  }

  try {
    const fn = new Function(
      problemType === 'fibonacci' ? 'n' : 'arr',
      `
      ${code}
      return ${functionName}(${problemType === 'fibonacci' ? 'n' : 'arr'});
    `
    );

    return testCases.map((testCase) => {
      try {
        const input = problemType === 'fibonacci' 
          ? parseInt(testCase.input)
          : JSON.parse(testCase.input);
        const expected = testCase.expectedOutput;

        const actual = fn(input);
        const actualStr = problemType === 'sortArray' 
          ? JSON.stringify(actual)
          : actual.toString();

        const passed = actualStr === expected;

        return {
          input: testCase.input,
          expectedOutput: expected,
          actualOutput: actualStr,
          passed,
          error: "",
        };
      } catch (error) {
        return {
          input: testCase.input,
          expectedOutput: testCase.expectedOutput,
          actualOutput: `Error: ${error instanceof Error ? error.message : String(error)}`,
          passed: false,
          error: `Error: ${error instanceof Error ? error.message : String(error)}`,
        };
      }
    });
  } catch (error) {
    return [
      {
        input: "N/A",
        expectedOutput: "N/A",
        actualOutput: `Error: ${error instanceof Error ? error.message : String(error)}`,
        passed: false,
        error: `Error: ${error instanceof Error ? error.message : String(error)}`,
      },
    ];
  }
}

// Legacy exports for backward compatibility
export { sumArrayTestCases as testCases };
export { runTests as runSumArrayTests };