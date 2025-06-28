# Topic API Documentation

This guide explains how to use the Topic API endpoints to manage topics within courses.

## Overview

Topics are the main organizational units within a course. Each topic contains multiple lessons and represents a specific subject area or learning module.

## Base URL

```
http://localhost:8000/topics
```

## Authentication

All endpoints require authentication. Include your authentication token in the request headers:

```
Authorization: Bearer <your_token>
```

## Endpoints

### 1. Create Topic

**POST** `/topics/`

Creates a new topic for a specific course.

#### Request Body

```json
{
  "name": "Introduction to Algorithms",
  "description": "Learn the fundamentals of algorithm design and analysis",
  "course_id": 1,
  "order": 1,
  "external_id": "algo-intro",
  "prerequisites": ["basic-programming", "math-fundamentals"]
}
```

#### Request Schema

| Field           | Type          | Required | Description                            |
| --------------- | ------------- | -------- | -------------------------------------- |
| `name`          | string        | Yes      | Topic name (1-255 characters)          |
| `description`   | string        | No       | Topic description                      |
| `course_id`     | integer       | Yes      | ID of the course this topic belongs to |
| `order`         | integer       | No       | Order within the course (default: 0)   |
| `external_id`   | string        | No       | External identifier for display        |
| `prerequisites` | array[string] | No       | List of prerequisite topics            |

#### Response

```json
{
  "id": 1,
  "name": "Introduction to Algorithms",
  "description": "Learn the fundamentals of algorithm design and analysis",
  "course_id": 1,
  "order": 1,
  "external_id": "algo-intro",
  "prerequisites": ["basic-programming", "math-fundamentals"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Example with cURL

```bash
curl -X POST "http://localhost:8000/topics/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Introduction to Algorithms",
    "description": "Learn the fundamentals of algorithm design and analysis",
    "course_id": 1,
    "order": 1,
    "external_id": "algo-intro"
  }'
```

### 2. List Topics for Course

**GET** `/topics/course/{course_id}`

Retrieves all topics for a specific course, ordered by their sequence.

#### Path Parameters

| Parameter   | Type    | Description      |
| ----------- | ------- | ---------------- |
| `course_id` | integer | ID of the course |

#### Response

```json
[
  {
    "id": 1,
    "name": "Introduction to Algorithms",
    "description": "Learn the fundamentals of algorithm design and analysis",
    "course_id": 1,
    "order": 1,
    "external_id": "algo-intro",
    "prerequisites": ["basic-programming"],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Data Structures",
    "description": "Understanding fundamental data structures",
    "course_id": 1,
    "order": 2,
    "external_id": "data-structures",
    "prerequisites": ["algo-intro"],
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  }
]
```

#### Example with cURL

```bash
curl -X GET "http://localhost:8000/topics/course/1" \
  -H "Authorization: Bearer your_token_here"
```

### 3. Get Topic by ID

**GET** `/topics/{topic_id}`

Retrieves a specific topic by its ID.

#### Path Parameters

| Parameter  | Type    | Description     |
| ---------- | ------- | --------------- |
| `topic_id` | integer | ID of the topic |

#### Response

```json
{
  "id": 1,
  "name": "Introduction to Algorithms",
  "description": "Learn the fundamentals of algorithm design and analysis",
  "course_id": 1,
  "order": 1,
  "external_id": "algo-intro",
  "prerequisites": ["basic-programming"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Example with cURL

```bash
curl -X GET "http://localhost:8000/topics/1" \
  -H "Authorization: Bearer your_token_here"
```

### 4. Get Topic with Lessons

**GET** `/topics/{topic_id}/with-lessons`

Retrieves a topic along with all its associated lessons.

#### Path Parameters

| Parameter  | Type    | Description     |
| ---------- | ------- | --------------- |
| `topic_id` | integer | ID of the topic |

#### Response

```json
{
  "id": 1,
  "name": "Introduction to Algorithms",
  "description": "Learn the fundamentals of algorithm design and analysis",
  "course_id": 1,
  "order": 1,
  "external_id": "algo-intro",
  "prerequisites": ["basic-programming"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "lessons": [
    {
      "id": 1,
      "external_id": "lesson-1",
      "title": "What are Algorithms?",
      "description": "Introduction to the concept of algorithms",
      "topic_id": 1,
      "order": 1,
      "next_lesson_id": "lesson-2",
      "prev_lesson_id": null,
      "sections": [
        {
          "type": "text",
          "content": "An algorithm is a step-by-step procedure...",
          "order": 1,
          "options": null,
          "answer": null,
          "explanation": null
        }
      ]
    },
    {
      "id": 2,
      "external_id": "lesson-2",
      "title": "Algorithm Complexity",
      "description": "Understanding time and space complexity",
      "topic_id": 1,
      "order": 2,
      "next_lesson_id": "lesson-3",
      "prev_lesson_id": "lesson-1",
      "sections": []
    }
  ]
}
```

#### Example with cURL

```bash
curl -X GET "http://localhost:8000/topics/1/with-lessons" \
  -H "Authorization: Bearer your_token_here"
```

### 5. Update Topic

**PUT** `/topics/{topic_id}`

Updates an existing topic. Only provided fields will be updated.

#### Path Parameters

| Parameter  | Type    | Description               |
| ---------- | ------- | ------------------------- |
| `topic_id` | integer | ID of the topic to update |

#### Request Body

```json
{
  "name": "Advanced Algorithm Design",
  "description": "Advanced concepts in algorithm design and optimization",
  "order": 3,
  "prerequisites": ["algo-intro", "data-structures"]
}
```

#### Request Schema

| Field           | Type          | Required | Description                   |
| --------------- | ------------- | -------- | ----------------------------- |
| `name`          | string        | No       | Topic name (1-255 characters) |
| `description`   | string        | No       | Topic description             |
| `order`         | integer       | No       | Order within the course       |
| `prerequisites` | array[string] | No       | List of prerequisite topics   |

#### Response

```json
{
  "id": 1,
  "name": "Advanced Algorithm Design",
  "description": "Advanced concepts in algorithm design and optimization",
  "course_id": 1,
  "order": 3,
  "external_id": "algo-intro",
  "prerequisites": ["algo-intro", "data-structures"],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

#### Example with cURL

```bash
curl -X PUT "http://localhost:8000/topics/1" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Advanced Algorithm Design",
    "description": "Advanced concepts in algorithm design and optimization",
    "order": 3
  }'
```

### 6. Delete Topic

**DELETE** `/topics/{topic_id}`

Deletes a topic and all its associated lessons.

#### Path Parameters

| Parameter  | Type    | Description               |
| ---------- | ------- | ------------------------- |
| `topic_id` | integer | ID of the topic to delete |

#### Response

- **Status Code**: 204 No Content
- **Body**: Empty

#### Example with cURL

```bash
curl -X DELETE "http://localhost:8000/topics/1" \
  -H "Authorization: Bearer your_token_here"
```

## Error Responses

### 404 Not Found

```json
{
  "detail": "Topic not found"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Best Practices

1. **Topic Ordering**: Use the `order` field to maintain a logical sequence of topics within a course.

2. **Prerequisites**: Use the `prerequisites` field to define dependencies between topics.

3. **External IDs**: Use meaningful `external_id` values for better user experience and URL-friendly identifiers.

4. **Descriptions**: Provide clear, concise descriptions for each topic to help learners understand what they'll learn.

5. **Error Handling**: Always check for error responses and handle them appropriately in your application.

## Complete Workflow Example

Here's a complete example of creating a course structure:

1. **Create Course** (using Course API)
2. **Create Topics** for the course
3. **Create Lessons** for each topic
4. **Retrieve Topics with Lessons** to display the complete structure

```bash
# 1. Create a course
curl -X POST "http://localhost:8000/courses/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Data Structures and Algorithms",
    "description": "Comprehensive course on DSA",
    "level": "Intermediate"
  }'

# 2. Create topics for the course
curl -X POST "http://localhost:8000/topics/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Introduction to Algorithms",
    "description": "Basic algorithm concepts",
    "course_id": 1,
    "order": 1
  }'

# 3. Get topics with lessons
curl -X GET "http://localhost:8000/topics/1/with-lessons" \
  -H "Authorization: Bearer your_token_here"
```
