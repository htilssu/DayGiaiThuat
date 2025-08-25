"use client";

import { useState } from "react";
import { ChatMessage } from "@/lib/api/chat";
import { topicsApi, lessonsApi, exercisesApi, quizzesApi } from "@/lib/api";
import { ContentType, ContentFormData } from "./types";

export function useContentCreation() {
  const [formData, setFormData] = useState<ContentFormData>({
    topic: {
      name: "",
      description: "",
      courseId: 1,
      order: 1,
      externalId: "",
    },
    lesson: {
      title: "",
      description: "",
      topicId: 1,
      order: 1,
      externalId: "",
      difficultyLevel: "beginner",
      lessonType: "theory",
      includeExamples: true,
      includeExercises: true,
      maxSections: 5,
    },
    exercise: {
      lessonId: 1,
      difficulty: "beginner",
      sessionId: "",
    },
    quiz: {
      lessonId: 1,
      questionCount: 5,
      difficulty: "beginner",
    },
  });

  const resetFormData = () => {
    setFormData({
      topic: {
        name: "",
        description: "",
        courseId: 1,
        order: 1,
        externalId: "",
      },
      lesson: {
        title: "",
        description: "",
        topicId: 1,
        order: 1,
        externalId: "",
        difficultyLevel: "beginner",
        lessonType: "theory",
        includeExamples: true,
        includeExercises: true,
        maxSections: 5,
      },
      exercise: {
        lessonId: 1,
        difficulty: "beginner",
        sessionId: "",
      },
      quiz: {
        lessonId: 1,
        questionCount: 5,
        difficulty: "beginner",
      },
    });
  };

  const validateForm = (
    contentType: ContentType
  ): { isValid: boolean; errorMessage: string } => {
    switch (contentType) {
      case "topic":
        if (!formData.topic.name.trim()) {
          return { isValid: false, errorMessage: "Topic name is required" };
        }
        break;
      case "lesson":
        if (!formData.lesson.title.trim()) {
          return { isValid: false, errorMessage: "Lesson title is required" };
        }
        break;
      case "exercise":
        if (!formData.exercise.sessionId.trim()) {
          return { isValid: false, errorMessage: "Session ID is required" };
        }
        break;
      case "quiz":
        if (formData.quiz.questionCount < 1) {
          return {
            isValid: false,
            errorMessage: "Question count must be at least 1",
          };
        }
        break;
    }
    return { isValid: true, errorMessage: "" };
  };

  const createContent = async (
    contentType: ContentType,
    onSuccess: (message: ChatMessage) => void,
    onError: (message: ChatMessage) => void
  ) => {
    const validation = validateForm(contentType);
    if (!validation.isValid) {
      onError({
        role: "assistant",
        content: `❌ Validation error: ${validation.errorMessage}`,
        timestamp: new Date().toISOString(),
      });
      return;
    }

    try {
      let response;
      let successMessage: ChatMessage;

      switch (contentType) {
        case "topic":
          response = await topicsApi.createTopic({
            name: formData.topic.name,
            description: formData.topic.description,
            courseId: formData.topic.courseId,
            order: formData.topic.order,
            lessons: [],
          });
          successMessage = {
            role: "assistant",
            content: `✅ Topic "${response.name}" created successfully!`,
            timestamp: new Date().toISOString(),
          };
          break;

        case "lesson":
          response = await lessonsApi.generateLesson(
            formData.lesson.topicId,
            formData.lesson.order,
            {
              topicName: formData.lesson.title,
              lessonTitle: formData.lesson.title,
              lessonDescription: formData.lesson.description,
              difficultyLevel: formData.lesson.difficultyLevel,
              lessonType: formData.lesson.lessonType,
              includeExamples: formData.lesson.includeExamples,
              includeExercises: formData.lesson.includeExercises,
              maxSections: formData.lesson.maxSections,
            }
          );
          successMessage = {
            role: "assistant",
            content: `✅ Lesson "${response.title}" generated successfully!`,
            timestamp: new Date().toISOString(),
          };
          break;

        case "exercise":
          response = await exercisesApi.createExercise({
            lessonId: formData.exercise.lessonId,
            difficulty: formData.exercise.difficulty,
            sessionId: formData.exercise.sessionId,
            topicId: formData.exercise.topicId || formData.lesson.topicId,
          });
          successMessage = {
            role: "assistant",
            content: `✅ Exercise "${
              response.title || response.name || "Untitled"
            }" created successfully!`,
            timestamp: new Date().toISOString(),
          };
          break;

        case "quiz":
          response = await quizzesApi.createQuiz({
            lessonId: formData.quiz.lessonId,
            questionCount: formData.quiz.questionCount,
            difficulty: formData.quiz.difficulty,
          });
          successMessage = {
            role: "assistant",
            content: `✅ Quiz created successfully with ${response.questions.length} questions!`,
            timestamp: new Date().toISOString(),
          };
          break;

        default:
          onError({
            role: "assistant",
            content: "❌ Unknown content type",
            timestamp: new Date().toISOString(),
          });
          return;
      }

      onSuccess(successMessage);
    } catch (error) {
      console.error("Error creating content:", error);
      let errorMsg = "Unknown error";
      if (error && typeof error === "object") {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const err = error as any;
        if (err.data && err.data.detail) {
          errorMsg = err.data.detail;
        } else if (err.message) {
          errorMsg = err.message;
        } else {
          try {
            errorMsg = JSON.stringify(error);
          } catch {
            errorMsg = String(error);
          }
        }
      } else {
        errorMsg = String(error);
      }
      onError({
        role: "assistant",
        content: `❌ Error creating ${contentType}: ${errorMsg}`,
        timestamp: new Date().toISOString(),
      });
    }
  };

  return {
    formData,
    setFormData,
    resetFormData,
    createContent,
  };
}
