import {
  Stack,
  TextInput,
  Textarea,
  NumberInput,
  Select,
  Checkbox,
} from "@mantine/core";
import { ContentType, ContentFormData } from "./types";
import { useEffect, useState } from "react";
import { coursesApi, topicsApi, lessonsApi } from "../../lib/api";
import { v4 as uuidv4 } from "uuid";

interface ContentFormProps {
  contentType: ContentType;
  formData: ContentFormData;
  onFormDataChange: (formData: ContentFormData) => void;
}

export function ContentForm({
  contentType,
  formData,
  onFormDataChange,
}: ContentFormProps) {
  const updateFormData = <K extends keyof ContentFormData>(
    key: K,
    value: ContentFormData[K]
  ) => {
    onFormDataChange({
      ...formData,
      [key]: value,
    });
  };

  const updateTopicData = (
    field: keyof ContentFormData["topic"],
    value: any
  ) => {
    updateFormData("topic", {
      ...formData.topic,
      [field]: value,
    });
  };

  const updateLessonData = (
    field: keyof ContentFormData["lesson"],
    value: any
  ) => {
    updateFormData("lesson", {
      ...formData.lesson,
      [field]: value,
    });
  };

  const updateExerciseData = (
    field: keyof ContentFormData["exercise"],
    value: any
  ) => {
    updateFormData("exercise", {
      ...formData.exercise,
      [field]: value,
    });
  };

  const updateQuizData = (field: keyof ContentFormData["quiz"], value: any) => {
    updateFormData("quiz", {
      ...formData.quiz,
      [field]: value,
    });
  };

  // Add state for courses, topics, and lessons
  const [courses, setCourses] = useState<{ id: number; title: string }[]>([]);
  const [topics, setTopics] = useState<{ id: number; name: string }[]>([]);
  const [lessons, setLessons] = useState<{ id: number; title: string }[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [selectedTopicId, setSelectedTopicId] = useState<number | null>(null);

  // Fetch courses on mount
  useEffect(() => {
    coursesApi
      .getCourses(1, 100)
      .then((res: { items: { id: number; title: string }[] }) => {
        setCourses(res.items || []);
        if (res.items && res.items.length > 0 && !selectedCourseId) {
          setSelectedCourseId(res.items[0].id);
        }
      });
    // eslint-disable-next-line
  }, []);

  // Fetch topics when selectedCourseId changes
  useEffect(() => {
    if (selectedCourseId) {
      topicsApi
        .getTopicsByCourse(selectedCourseId)
        .then((res: { id: number; name: string }[]) => {
          setTopics(res || []);
          if (res && res.length > 0 && !selectedTopicId) {
            setSelectedTopicId(res[0].id);
          }
          // Auto-set topic order to topics.length + 1
          if (contentType === "topic") {
            updateTopicData("order", (res?.length || 0) + 1);
          }
        });
    }
    // eslint-disable-next-line
  }, [selectedCourseId, contentType]);

  // Fetch lessons when selectedTopicId changes
  useEffect(() => {
    if (selectedTopicId) {
      lessonsApi
        .getLessonsByTopic(selectedTopicId)
        .then((res: { id: number; title: string }[]) => {
          setLessons(res || []);
          if (res && res.length > 0 && !formData.exercise.lessonId) {
            updateExerciseData("lessonId", res[0].id);
          }
          // Auto-set lesson order to lessons.length + 1
          if (contentType === "lesson") {
            updateLessonData("order", (res?.length || 0) + 1);
          }
        });
    }
    // eslint-disable-next-line
  }, [selectedTopicId, contentType]);

  // Auto-generate sessionId when lesson changes or on mount
  useEffect(() => {
    if (!formData.exercise.sessionId || formData.exercise.lessonId) {
      updateExerciseData("sessionId", uuidv4());
    }
    // eslint-disable-next-line
  }, [formData.exercise.lessonId]);

  switch (contentType) {
    case "topic":
      return (
        <Stack gap="md">
          <TextInput
            label="Topic Name"
            placeholder="Enter topic name"
            value={formData.topic.name}
            onChange={(e) => updateTopicData("name", e.target.value)}
            required
          />
          <Textarea
            label="Description"
            placeholder="Enter topic description"
            value={formData.topic.description}
            onChange={(e) => updateTopicData("description", e.target.value)}
            rows={3}
          />
          <Select
            label="Course"
            placeholder="Select course"
            data={courses.map((c) => ({
              value: c.id.toString(),
              label: c.title,
            }))}
            value={
              formData.topic.courseId
                ? formData.topic.courseId.toString()
                : undefined
            }
            onChange={(value) => {
              const id = value ? parseInt(value) : 0;
              updateTopicData("courseId", id);
              setSelectedCourseId(id);
            }}
            required
          />
          <NumberInput
            label="Order"
            placeholder="Order will be set automatically"
            value={formData.topic.order}
            readOnly
            disabled
            required
          />
          <TextInput
            label="External ID"
            placeholder="Enter external ID"
            value={formData.topic.externalId}
            onChange={(e) => updateTopicData("externalId", e.target.value)}
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
            onChange={(e) => updateLessonData("title", e.target.value)}
            required
          />
          <Textarea
            label="Description"
            placeholder="Enter lesson description"
            value={formData.lesson.description}
            onChange={(e) => updateLessonData("description", e.target.value)}
            rows={3}
          />
          <Select
            label="Course"
            placeholder="Select course"
            data={courses.map((c) => ({
              value: c.id.toString(),
              label: c.title,
            }))}
            value={selectedCourseId ? selectedCourseId.toString() : undefined}
            onChange={(value) => {
              const id = value ? parseInt(value) : 0;
              setSelectedCourseId(id);
            }}
            required
          />
          <Select
            label="Topic"
            placeholder="Select topic"
            data={topics.map((t) => ({
              value: t.id.toString(),
              label: t.name,
            }))}
            value={
              formData.lesson.topicId
                ? formData.lesson.topicId.toString()
                : undefined
            }
            onChange={(value) => {
              const id = value ? parseInt(value) : 0;
              updateLessonData("topicId", id);
              setSelectedTopicId(id);
            }}
            required
          />
          <NumberInput
            label="Order"
            placeholder="Order will be set automatically"
            value={formData.lesson.order}
            readOnly
            disabled
            required
          />
          <TextInput
            label="External ID"
            placeholder="Enter external ID"
            value={formData.lesson.externalId}
            onChange={(e) => updateLessonData("externalId", e.target.value)}
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
              updateLessonData("difficultyLevel", value || "beginner")
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
              updateLessonData("lessonType", value || "theory")
            }
          />
          <Checkbox
            label="Include Examples"
            checked={formData.lesson.includeExamples}
            onChange={(e) =>
              updateLessonData("includeExamples", e.currentTarget.checked)
            }
            color="teal"
          />
          <Checkbox
            label="Include Exercises"
            checked={formData.lesson.includeExercises}
            onChange={(e) =>
              updateLessonData("includeExercises", e.currentTarget.checked)
            }
            color="teal"
          />
          <NumberInput
            label="Max Sections"
            placeholder="Enter max sections"
            value={formData.lesson.maxSections}
            onChange={(value) =>
              updateLessonData(
                "maxSections",
                typeof value === "number" ? value : 5
              )
            }
          />
        </Stack>
      );

    case "exercise":
      return (
        <Stack gap="md">
          <Select
            label="Course"
            placeholder="Select course"
            data={courses.map((c) => ({
              value: c.id.toString(),
              label: c.title,
            }))}
            value={selectedCourseId ? selectedCourseId.toString() : undefined}
            onChange={(value) => {
              const id = value ? parseInt(value) : 0;
              setSelectedCourseId(id);
              setSelectedTopicId(null);
              setLessons([]);
            }}
            required
          />
          <Select
            label="Topic"
            placeholder="Select topic"
            data={topics.map((t) => ({
              value: t.id.toString(),
              label: t.name,
            }))}
            value={selectedTopicId ? selectedTopicId.toString() : undefined}
            onChange={(value) => {
              const id = value ? parseInt(value) : 0;
              setSelectedTopicId(id);
              setLessons([]);
              updateExerciseData("topicId", id);
            }}
            required
          />
          <Select
            label="Lesson"
            placeholder="Select lesson"
            data={lessons.map((l) => ({
              value: l.id.toString(),
              label: l.title,
            }))}
            value={
              formData.exercise.lessonId
                ? formData.exercise.lessonId.toString()
                : undefined
            }
            onChange={(value) => {
              const id = value ? parseInt(value) : 0;
              updateExerciseData("lessonId", id);
            }}
            required
          />
          <TextInput
            label="Session ID"
            value={formData.exercise.sessionId}
            readOnly
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
              updateExerciseData("difficulty", value || "beginner")
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
              updateQuizData("lessonId", typeof value === "number" ? value : 1)
            }
            required
          />
          <NumberInput
            label="Question Count"
            placeholder="Enter number of questions"
            value={formData.quiz.questionCount}
            onChange={(value) =>
              updateQuizData(
                "questionCount",
                typeof value === "number" ? value : 5
              )
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
              updateQuizData("difficulty", value || "beginner")
            }
          />
        </Stack>
      );

    default:
      return null;
  }
}
