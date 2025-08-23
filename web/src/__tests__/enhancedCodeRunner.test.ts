/**
 * Tests for the enhanced code runner
 * These are example tests that would run in a Jest or similar environment
 */

import { 
  runTests, 
  runTestsForProblem, 
  sumArrayTestCases, 
  fibonacciTestCases,
  sortArrayTestCases 
} from '../services/enhancedCodeRunner';

describe('Enhanced Code Runner', () => {
  describe('Sum Array Tests', () => {
    it('should correctly test a working sumArray implementation', () => {
      const code = `
        function sumArray(arr) {
          return arr.reduce((a, b) => a + b, 0);
        }
      `;

      const results = runTests(code, sumArrayTestCases);
      
      // All tests should pass for correct implementation
      const allPassed = results.every(result => result.passed);
      expect(allPassed).toBe(true);
      
      // Should have same number of results as test cases
      expect(results.length).toBe(sumArrayTestCases.length);
    });

    it('should correctly fail tests for incorrect implementation', () => {
      const code = `
        function sumArray(arr) {
          return arr.length; // Wrong implementation
        }
      `;

      const results = runTests(code, sumArrayTestCases);
      
      // Most tests should fail for incorrect implementation
      const failedCount = results.filter(result => !result.passed).length;
      expect(failedCount).toBeGreaterThan(5);
    });

    it('should handle syntax errors gracefully', () => {
      const code = `
        function sumArray(arr) {
          return arr.reduce((a, b) => a + b, 0;  // Missing closing parenthesis
        }
      `;

      const results = runTests(code, sumArrayTestCases);
      
      // Should return error results
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].error).toContain('Error');
    });
  });

  describe('Multi-Problem Support', () => {
    it('should correctly test fibonacci implementation', () => {
      const code = `
        function fibonacci(n) {
          if (n <= 1) return n;
          return fibonacci(n - 1) + fibonacci(n - 2);
        }
      `;

      const results = runTestsForProblem(code, 'fibonacci');
      
      const allPassed = results.every(result => result.passed);
      expect(allPassed).toBe(true);
    });

    it('should correctly test sort array implementation', () => {
      const code = `
        function sortArray(arr) {
          return [...arr].sort((a, b) => a - b);
        }
      `;

      const results = runTestsForProblem(code, 'sortArray');
      
      const allPassed = results.every(result => result.passed);
      expect(allPassed).toBe(true);
    });

    it('should handle unknown problem types', () => {
      const code = `function test() { return 42; }`;
      
      expect(() => {
        runTestsForProblem(code, 'unknownProblem' as any);
      }).toThrow('Unknown problem type');
    });
  });

  describe('Custom Test Cases', () => {
    it('should accept custom test cases', () => {
      const customTestCases = [
        { input: "[1, 2]", expectedOutput: "3" },
        { input: "[10, 20]", expectedOutput: "30" }
      ];

      const code = `
        function sumArray(arr) {
          return arr.reduce((a, b) => a + b, 0);
        }
      `;

      const results = runTestsForProblem(code, 'sumArray', customTestCases);
      
      expect(results.length).toBe(2);
      expect(results.every(result => result.passed)).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('should handle runtime errors in user code', () => {
      const code = `
        function sumArray(arr) {
          throw new Error("User error");
        }
      `;

      const results = runTests(code, [{ input: "[1, 2, 3]", expectedOutput: "6" }]);
      
      expect(results[0].passed).toBe(false);
      expect(results[0].error).toContain('User error');
    });

    it('should handle invalid JSON in test cases', () => {
      const code = `
        function sumArray(arr) {
          return arr.reduce((a, b) => a + b, 0);
        }
      `;

      const results = runTests(code, [{ input: "invalid json", expectedOutput: "0" }]);
      
      expect(results[0].passed).toBe(false);
      expect(results[0].error).toContain('Error');
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty code', () => {
      const results = runTests('', sumArrayTestCases);
      
      expect(results.length).toBeGreaterThan(0);
      expect(results[0].error).toContain('Error');
    });

    it('should handle missing function definition', () => {
      const code = `
        // No sumArray function defined
        console.log("hello");
      `;

      const results = runTests(code, [{ input: "[1, 2, 3]", expectedOutput: "6" }]);
      
      expect(results[0].passed).toBe(false);
      expect(results[0].error).toContain('Error');
    });
  });
});

// Additional manual test function for demonstration
export function manualTestExample() {
  console.log('Running manual test example...');
  
  const correctCode = `
    function sumArray(arr) {
      return arr.reduce((a, b) => a + b, 0);
    }
  `;

  const testCase = { input: "[1, 2, 3, 4, 5]", expectedOutput: "15" };
  const results = runTests(correctCode, [testCase]);
  
  console.log('Test Result:', results[0]);
  console.log('Passed:', results[0].passed);
  
  return results[0].passed;
}

// Performance test
export function performanceTest() {
  const code = `
    function sumArray(arr) {
      return arr.reduce((a, b) => a + b, 0);
    }
  `;

  const largeTestCase = {
    input: JSON.stringify(Array.from({ length: 10000 }, (_, i) => i)),
    expectedOutput: (10000 * 9999 / 2).toString()
  };

  const startTime = performance.now();
  const results = runTests(code, [largeTestCase]);
  const endTime = performance.now();

  console.log(`Performance test completed in ${endTime - startTime} ms`);
  console.log('Result:', results[0].passed);
  
  return {
    passed: results[0].passed,
    duration: endTime - startTime
  };
}