import { useState, useRef, useEffect } from "react";
import {
  Box,
  Paper,
  TextInput,
  ActionIcon,
  LoadingOverlay,
  Button,
  Group,
  Text,
  Modal,
  Textarea,
  Select,
  NumberInput,
  Stack,
  Divider,
} from "@mantine/core";
import {
  IconSend,
  IconBook,
  IconFileText,
  IconBrain,
  IconQuestionMark,
  IconPlus,
  IconX,
} from "@tabler/icons-react";
import { ChatMessage as ChatMessageComponent } from "./ChatMessage";
import { ChatMessage } from "@/lib/api/chat";
import { GoogleGenAI } from "@google/genai";
import { topicsApi, lessonsApi, exercisesApi, quizzesApi } from "@/lib/api";

type ContentType = "topic" | "lesson" | "exercise" | "quiz";

interface ContentFormData {
  topic: {
    name: string;
    description: string;
    courseId: number;
    order: number;
    externalId: string;
  };
  lesson: {
    title: string;
    description: string;
    topicId: number;
    order: number;
    externalId: string;
    difficultyLevel: string;
    lessonType: string;
    includeExamples: boolean;
    includeExercises: boolean;
    maxSections: number;
  };
  exercise: {
    lessonId: number;
    difficulty: string;
    sessionId: string;
  };
  quiz: {
    lessonId: number;
    questionCount: number;
    difficulty: string;
  };
}

export function AdminChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showContentModal, setShowContentModal] = useState(false);
  const [selectedContentType, setSelectedContentType] =
    useState<ContentType | null>(null);
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
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const ai = new GoogleGenAI({
    apiKey: "AIzaSyAoWvIFmtiL1MwP1y8ariEm61Zaq4-uNZo",
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-05-20",
        contents: input,
        config: {
          systemInstruction:
            "You are a professional algorithm expert. You professionally create algorithm exercises. Your mission is to think of clear, concise and life related topic for the student to practice algorithm.",
        },
      });
      if (response.text) {
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: response.text,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCreateContent = async () => {
    if (!selectedContentType) return;

    // Validate required fields based on content type
    let isValid = true;
    let errorMessage = "";

    switch (selectedContentType) {
      case "topic":
        if (!formData.topic.name.trim()) {
          isValid = false;
          errorMessage = "Topic name is required";
        }
        break;
      case "lesson":
        if (!formData.lesson.title.trim()) {
          isValid = false;
          errorMessage = "Lesson title is required";
        }
        break;
      case "exercise":
        if (!formData.exercise.sessionId.trim()) {
          isValid = false;
          errorMessage = "Session ID is required";
        }
        break;
      case "quiz":
        if (formData.quiz.questionCount < 1) {
          isValid = false;
          errorMessage = "Question count must be at least 1";
        }
        break;
    }

    if (!isValid) {
      const errorMsg: ChatMessage = {
        role: "assistant",
        content: `❌ Validation error: ${errorMessage}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
      return;
    }

    setIsLoading(true);
    const userMessage: ChatMessage = {
      role: "user",
      content: `Creating ${selectedContentType}...`,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setShowContentModal(false);

    try {
      let response;
      let assistantMessage: ChatMessage;

      switch (selectedContentType) {
        case "topic":
          response = await topicsApi.createTopic({
            name: formData.topic.name,
            description: formData.topic.description,
            course_id: formData.topic.courseId,
            order: formData.topic.order,
            external_id: formData.topic.externalId,
          });
          assistantMessage = {
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
              topic_name: formData.lesson.title,
              lesson_title: formData.lesson.title,
              lesson_description: formData.lesson.description,
              difficulty_level: formData.lesson.difficultyLevel,
              lesson_type: formData.lesson.lessonType,
              include_examples: formData.lesson.includeExamples,
              include_exercises: formData.lesson.includeExercises,
              max_sections: formData.lesson.maxSections,
            }
          );
          assistantMessage = {
            role: "assistant",
            content: `✅ Lesson "${response.title}" generated successfully!`,
            timestamp: new Date().toISOString(),
          };
          break;

        case "exercise":
          response = await exercisesApi.createExercise({
            lesson_id: formData.exercise.lessonId,
            difficulty: formData.exercise.difficulty,
            session_id: formData.exercise.sessionId,
          });
          assistantMessage = {
            role: "assistant",
            content: `✅ Exercise "${response.name}" created successfully!`,
            timestamp: new Date().toISOString(),
          };
          break;

        case "quiz":
          response = await quizzesApi.createQuiz({
            lesson_id: formData.quiz.lessonId,
            question_count: formData.quiz.questionCount,
            difficulty: formData.quiz.difficulty,
          });
          assistantMessage = {
            role: "assistant",
            content: `✅ Quiz created successfully with ${response.questions.length} questions!`,
            timestamp: new Date().toISOString(),
          };
          break;

        default:
          assistantMessage = {
            role: "assistant",
            content: "❌ Unknown content type",
            timestamp: new Date().toISOString(),
          };
      }

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error creating content:", error);
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: `❌ Error creating ${selectedContentType}: ${error}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      resetFormData();
    }
  };

  const renderContentForm = () => {
    switch (selectedContentType) {
      case "topic":
        return (
          <Stack gap="md">
            <TextInput
              label="Topic Name"
              placeholder="Enter topic name"
              value={formData.topic.name}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  topic: { ...prev.topic, name: e.target.value },
                }))
              }
              required
            />
            <Textarea
              label="Description"
              placeholder="Enter topic description"
              value={formData.topic.description}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  topic: { ...prev.topic, description: e.target.value },
                }))
              }
              rows={3}
            />
            <NumberInput
              label="Course ID"
              placeholder="Enter course ID"
              value={formData.topic.courseId}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  topic: {
                    ...prev.topic,
                    courseId: typeof value === "number" ? value : 1,
                  },
                }))
              }
              required
            />
            <NumberInput
              label="Order"
              placeholder="Enter order"
              value={formData.topic.order}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  topic: {
                    ...prev.topic,
                    order: typeof value === "number" ? value : 1,
                  },
                }))
              }
              required
            />
            <TextInput
              label="External ID"
              placeholder="Enter external ID"
              value={formData.topic.externalId}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  topic: { ...prev.topic, externalId: e.target.value },
                }))
              }
            />
          </Stack>
        );

      case "lesson":
        return (
          <Stack gap="md">
            <TextInput
              label="Lesson Title"
              placeholder="Enter lesson title"
              value={formData.lesson.title}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: { ...prev.lesson, title: e.target.value },
                }))
              }
              required
            />
            <Textarea
              label="Description"
              placeholder="Enter lesson description"
              value={formData.lesson.description}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: { ...prev.lesson, description: e.target.value },
                }))
              }
              rows={3}
            />
            <NumberInput
              label="Topic ID"
              placeholder="Enter topic ID"
              value={formData.lesson.topicId}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: {
                    ...prev.lesson,
                    topicId: typeof value === "number" ? value : 1,
                  },
                }))
              }
              required
            />
            <NumberInput
              label="Order"
              placeholder="Enter order"
              value={formData.lesson.order}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: {
                    ...prev.lesson,
                    order: typeof value === "number" ? value : 1,
                  },
                }))
              }
              required
            />
            <TextInput
              label="External ID"
              placeholder="Enter external ID"
              value={formData.lesson.externalId}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: { ...prev.lesson, externalId: e.target.value },
                }))
              }
            />
            <Select
              label="Difficulty Level"
              data={[
                { value: "beginner", label: "Beginner" },
                { value: "intermediate", label: "Intermediate" },
                { value: "advanced", label: "Advanced" },
              ]}
              value={formData.lesson.difficultyLevel}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: {
                    ...prev.lesson,
                    difficultyLevel: value || "beginner",
                  },
                }))
              }
            />
            <Select
              label="Lesson Type"
              data={[
                { value: "theory", label: "Theory" },
                { value: "practice", label: "Practice" },
                { value: "mixed", label: "Mixed" },
              ]}
              value={formData.lesson.lessonType}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: { ...prev.lesson, lessonType: value || "theory" },
                }))
              }
            />
            <NumberInput
              label="Max Sections"
              placeholder="Enter max sections"
              value={formData.lesson.maxSections}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  lesson: {
                    ...prev.lesson,
                    maxSections: typeof value === "number" ? value : 5,
                  },
                }))
              }
            />
          </Stack>
        );

      case "exercise":
        return (
          <Stack gap="md">
            <NumberInput
              label="Lesson ID"
              placeholder="Enter lesson ID"
              value={formData.exercise.lessonId}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  exercise: {
                    ...prev.exercise,
                    lessonId: typeof value === "number" ? value : 1,
                  },
                }))
              }
              required
            />
            <Select
              label="Difficulty"
              data={[
                { value: "beginner", label: "Beginner" },
                { value: "intermediate", label: "Intermediate" },
                { value: "advanced", label: "Advanced" },
              ]}
              value={formData.exercise.difficulty}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  exercise: {
                    ...prev.exercise,
                    difficulty: value || "beginner",
                  },
                }))
              }
            />
            <TextInput
              label="Session ID"
              placeholder="Enter session ID"
              value={formData.exercise.sessionId}
              onChange={(e) =>
                setFormData((prev) => ({
                  ...prev,
                  exercise: { ...prev.exercise, sessionId: e.target.value },
                }))
              }
              required
            />
          </Stack>
        );

      case "quiz":
        return (
          <Stack gap="md">
            <NumberInput
              label="Lesson ID"
              placeholder="Enter lesson ID"
              value={formData.quiz.lessonId}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  quiz: {
                    ...prev.quiz,
                    lessonId: typeof value === "number" ? value : 1,
                  },
                }))
              }
              required
            />
            <NumberInput
              label="Question Count"
              placeholder="Enter number of questions"
              value={formData.quiz.questionCount}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  quiz: {
                    ...prev.quiz,
                    questionCount: typeof value === "number" ? value : 5,
                  },
                }))
              }
              required
            />
            <Select
              label="Difficulty"
              data={[
                { value: "beginner", label: "Beginner" },
                { value: "intermediate", label: "Intermediate" },
                { value: "advanced", label: "Advanced" },
              ]}
              value={formData.quiz.difficulty}
              onChange={(value) =>
                setFormData((prev) => ({
                  ...prev,
                  quiz: { ...prev.quiz, difficulty: value || "beginner" },
                }))
              }
            />
          </Stack>
        );

      default:
        return null;
    }
  };

  const contentOptions = [
    {
      type: "topic" as ContentType,
      icon: IconBook,
      label: "Create Topic",
      description: "Create a new topic for a course",
      color: "blue",
    },
    {
      type: "lesson" as ContentType,
      icon: IconFileText,
      label: "Create Lesson",
      description: "Generate a new lesson with AI",
      color: "green",
    },
    {
      type: "exercise" as ContentType,
      icon: IconBrain,
      label: "Create Exercise",
      description: "Create a new exercise",
      color: "orange",
    },
    {
      type: "quiz" as ContentType,
      icon: IconQuestionMark,
      label: "Create Quiz",
      description: "Create a new quiz",
      color: "purple",
    },
  ];

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

  const handleModalClose = () => {
    setShowContentModal(false);
    setSelectedContentType(null);
    resetFormData();
  };

  return (
    <>
      <Paper
        shadow="sm"
        p="md"
        style={{
          height: "600px",
          display: "flex",
          flexDirection: "column",
        }}>
        <Box
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "1rem",
            position: "relative",
          }}>
          <LoadingOverlay visible={isLoading} />
          {messages.map((message, index) => (
            <ChatMessageComponent key={index} message={message} />
          ))}
          <div ref={messagesEndRef} />
        </Box>

        <Divider my="md" />

        {/* Content Creation Options */}
        <Box mb="md">
          <Text size="sm" fw={500} mb="xs" c="dimmed">
            Create Content with AI
          </Text>
          <Group gap="xs">
            {contentOptions.map((option) => (
              <Button
                key={option.type}
                variant="light"
                size="xs"
                leftSection={<option.icon size={16} />}
                onClick={() => {
                  if (option.type) {
                    setSelectedContentType(option.type);
                    setShowContentModal(true);
                  }
                }}
                color={option.color || "blue"}
                style={{ flex: 1 }}>
                {option.label}
              </Button>
            ))}
          </Group>
        </Box>

        <Box p="xs">
          <TextInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Or type your message to chat with AI..."
            rightSection={
              <ActionIcon
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                variant="filled"
                size="lg">
                <IconSend size="1.2rem" />
              </ActionIcon>
            }
          />
        </Box>
      </Paper>

      {/* Content Creation Modal */}
      <Modal
        opened={showContentModal}
        onClose={handleModalClose}
        title={
          <Group>
            {selectedContentType &&
              (() => {
                const option = contentOptions.find(
                  (opt) => opt.type === selectedContentType
                );
                const IconComponent = option?.icon;
                return IconComponent ? <IconComponent size={20} /> : null;
              })()}
            <Text>
              Create{" "}
              {selectedContentType
                ? selectedContentType.charAt(0).toUpperCase() +
                  selectedContentType.slice(1)
                : ""}
            </Text>
          </Group>
        }
        size="lg"
        closeOnClickOutside={false}>
        <Box>
          {renderContentForm()}
          <Group justify="flex-end" mt="xl">
            <Button
              variant="light"
              onClick={handleModalClose}
              leftSection={<IconX size={16} />}>
              Cancel
            </Button>
            <Button
              onClick={handleCreateContent}
              leftSection={<IconPlus size={16} />}
              loading={isLoading}>
              Create{" "}
              {selectedContentType
                ? selectedContentType.charAt(0).toUpperCase() +
                  selectedContentType.slice(1)
                : ""}
            </Button>
          </Group>
        </Box>
      </Modal>
    </>
  );
}
