import type { Discussion } from "@/lib/api/discussions/types";

export const discussions: Discussion[] = [
  {
    id: 1,
    title: "How to solve binary search problems?",
    content:
      "I'm struggling with binary search. Any tips or recommended lessons? Check out [Lesson 101](/lessons/101) for a great explanation!",
    author: "Alice",
    createdAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    updatedAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    replies: 5,
    category: "Algorithms",
  },
  {
    id: 2,
    title: "Dynamic Programming vs Greedy Algorithms",
    content:
      "Can someone explain the difference between DP and greedy? Reference: [Lesson 202](/lessons/202)",
    author: "Bob",
    createdAt: new Date(Date.now() - 86400000 * 5).toISOString(),
    updatedAt: new Date(Date.now() - 86400000 * 4).toISOString(),
    replies: 8,
    category: "Theory",
  },
  {
    id: 3,
    title: "Best resources for learning recursion",
    content: "What are the best resources or lessons for recursion?",
    author: "Charlie",
    createdAt: new Date(Date.now() - 86400000 * 1).toISOString(),
    updatedAt: new Date(Date.now() - 86400000 * 1).toISOString(),
    replies: 2,
    category: "Algorithms",
  },
  {
    id: 4,
    title: "Tips for time complexity analysis",
    content: "How do you approach analyzing time complexity? Any lesson links?",
    author: "Dana",
    createdAt: new Date(Date.now() - 86400000 * 3).toISOString(),
    updatedAt: new Date(Date.now() - 86400000 * 2).toISOString(),
    replies: 3,
    category: "Complexity",
  },
  {
    id: 5,
    title: "Reference for sorting algorithms",
    content:
      "Is there a comprehensive lesson on sorting algorithms? See [Lesson 303](/lessons/303)",
    author: "Eve",
    createdAt: new Date(Date.now() - 86400000 * 7).toISOString(),
    updatedAt: new Date(Date.now() - 86400000 * 6).toISOString(),
    replies: 6,
    category: "Algorithms",
  },
];
