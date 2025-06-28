# Course API Documentation

This guide explains how to use the Course API endpoints to manage courses in the learning platform.

## Overview

Courses are the top-level organizational units that contain multiple topics. Each course represents a complete learning path or curriculum.

## Base URL

```
http://localhost:8000/courses
```

## Authentication

All endpoints require authentication. Include your authentication token in the request headers:

```
Authorization: Bearer <your_token>
```

## Endpoints

### 1. List Courses

**GET** `/courses`

Retrieves a paginated list of all courses.

#### Query Parameters

| Parameter | Type    | Default | Description                        |
| --------- | ------- | ------- | ---------------------------------- |
| `page`    | integer | 1       | Page number (starts from 1)        |
| `limit`   | integer | 10      | Number of items per page (max 100) |

#### Response

```json
{
  "items": [
    {
      "id": 1,
      "title": "Data Structures and Algorithms",
      "description": "Comprehensive course on fundamental data structures and algorithms",
      "thumbnail_url": "https://example.com/thumbnail.jpg",
      "level": "Intermediate",
      "duration": 1200,
      "price": 0.0,
      "is_published": true,
      "tags": "algorithms,data-structures,programming",
      "requirements": "Basic programming knowledge",
      "what_you_will_learn": "Master fundamental algorithms and data structures",
      "learning_path": "Beginner to Advanced",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    },
    {
      "id": 2,
      "title": "Web Development Fundamentals",
      "description": "Learn modern web development with HTML, CSS, and JavaScript",
      "thumbnail_url": "https://example.com/web-dev.jpg",
      "level": "Beginner",
      "duration": 800,
      "price": 0.0,
      "is_published": true,
      "tags": "web-development,html,css,javascript",
      "requirements": "No prior experience required",
      "what_you_will_learn": "Build responsive websites and web applications",
      "learning_path": "Complete Beginner",
      "created_at": "2024-01-15T11:00:00Z",
      "updated_at": "2024-01-15T11:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 10,
  "totalPages": 1
}
```

#### Example with cURL

```bash
curl -X GET "http://localhost:8000/courses?page=1&limit=10" \
  -H "Authorization: Bearer your_token_here"
```

### 2. Get Course by ID

**GET** `/courses/{course_id}`

Retrieves a specific course by its ID.

#### Path Parameters

| Parameter   | Type    | Description      |
| ----------- | ------- | ---------------- |
| `course_id` | integer | ID of the course |

#### Response

```json
{
  "id": 1,
  "title": "Data Structures and Algorithms",
  "description": "Comprehensive course on fundamental data structures and algorithms",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "level": "Intermediate",
  "duration": 1200,
  "price": 0.0,
  "is_published": true,
  "tags": "algorithms,data-structures,programming",
  "requirements": "Basic programming knowledge",
  "what_you_will_learn": "Master fundamental algorithms and data structures",
  "learning_path": "Beginner to Advanced",
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

#### Example with cURL

```bash
curl -X GET "http://localhost:8000/courses/1" \
  -H "Authorization: Bearer your_token_here"
```

### 3. Create Course

**POST** `/courses/`

Creates a new course.

#### Request Body

```json
{
  "title": "Machine Learning Fundamentals",
  "description": "Introduction to machine learning concepts and algorithms",
  "thumbnail_url": "https://example.com/ml-course.jpg",
  "level": "Advanced",
  "duration": 1800,
  "price": 99.99,
  "is_published": false,
  "tags": "machine-learning,ai,data-science",
  "requirements": "Python programming, basic statistics, linear algebra",
  "what_you_will_learn": "Build and deploy machine learning models",
  "learning_path": "Intermediate to Advanced"
}
```

#### Request Schema

| Field                 | Type    | Required | Description                                       |
| --------------------- | ------- | -------- | ------------------------------------------------- |
| `title`               | string  | Yes      | Course title (3-255 characters)                   |
| `description`         | string  | No       | Course description                                |
| `thumbnail_url`       | string  | No       | URL to course thumbnail image                     |
| `level`               | string  | No       | Difficulty level (Beginner/Intermediate/Advanced) |
| `duration`            | integer | No       | Estimated duration in minutes                     |
| `price`               | float   | No       | Course price (0.0 for free)                       |
| `is_published`        | boolean | No       | Publication status                                |
| `tags`                | string  | No       | Comma-separated tags                              |
| `requirements`        | string  | No       | Prerequisites as JSON string                      |
| `what_you_will_learn` | string  | No       | Learning outcomes as JSON string                  |
| `learning_path`       | string  | No       | Learning path description as JSON string          |

#### Response

```json
{
  "id": 3,
  "title": "Machine Learning Fundamentals",
  "description": "Introduction to machine learning concepts and algorithms",
  "thumbnail_url": "https://example.com/ml-course.jpg",
  "level": "Advanced",
  "duration": 1800,
  "price": 99.99,
  "is_published": false,
  "tags": "machine-learning,ai,data-science",
  "requirements": "Python programming, basic statistics, linear algebra",
  "what_you_will_learn": "Build and deploy machine learning models",
  "learning_path": "Intermediate to Advanced",
  "created_at": "2024-01-15T14:00:00Z",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

#### Example with cURL

```bash
curl -X POST "http://localhost:8000/courses/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Machine Learning Fundamentals",
    "description": "Introduction to machine learning concepts and algorithms",
    "level": "Advanced",
    "duration": 1800,
    "price": 99.99,
    "tags": "machine-learning,ai,data-science"
  }'
```

### 4. Update Course

**PUT** `/courses/{course_id}`

Updates an existing course. Only provided fields will be updated.

#### Path Parameters

| Parameter   | Type    | Description                |
| ----------- | ------- | -------------------------- |
| `course_id` | integer | ID of the course to update |

#### Request Body

```json
{
  "title": "Advanced Machine Learning",
  "description": "Advanced machine learning techniques and deep learning",
  "level": "Advanced",
  "price": 149.99,
  "is_published": true
}
```

#### Request Schema

| Field                 | Type    | Required | Description                              |
| --------------------- | ------- | -------- | ---------------------------------------- |
| `title`               | string  | No       | Course title (3-255 characters)          |
| `description`         | string  | No       | Course description                       |
| `thumbnail_url`       | string  | No       | URL to course thumbnail image            |
| `level`               | string  | No       | Difficulty level                         |
| `duration`            | integer | No       | Estimated duration in minutes            |
| `price`               | float   | No       | Course price                             |
| `is_published`        | boolean | No       | Publication status                       |
| `tags`                | string  | No       | Comma-separated tags                     |
| `requirements`        | string  | No       | Prerequisites as JSON string             |
| `what_you_will_learn` | string  | No       | Learning outcomes as JSON string         |
| `learning_path`       | string  | No       | Learning path description as JSON string |

#### Response

```json
{
  "id": 3,
  "title": "Advanced Machine Learning",
  "description": "Advanced machine learning techniques and deep learning",
  "thumbnail_url": "https://example.com/ml-course.jpg",
  "level": "Advanced",
  "duration": 1800,
  "price": 149.99,
  "is_published": true,
  "tags": "machine-learning,ai,data-science",
  "requirements": "Python programming, basic statistics, linear algebra",
  "what_you_will_learn": "Build and deploy machine learning models",
  "learning_path": "Intermediate to Advanced",
  "created_at": "2024-01-15T14:00:00Z",
  "updated_at": "2024-01-15T15:00:00Z"
}
```

#### Example with cURL

```bash
curl -X PUT "http://localhost:8000/courses/3" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Machine Learning",
    "description": "Advanced machine learning techniques and deep learning",
    "price": 149.99,
    "is_published": true
  }'
```

### 5. Delete Course

**DELETE** `/courses/{course_id}`

Deletes a course and all its associated topics and lessons.

#### Path Parameters

| Parameter   | Type    | Description                |
| ----------- | ------- | -------------------------- |
| `course_id` | integer | ID of the course to delete |

#### Response

- **Status Code**: 204 No Content
- **Body**: Empty

#### Example with cURL

```bash
curl -X DELETE "http://localhost:8000/courses/3" \
  -H "Authorization: Bearer your_token_here"
```

## Error Responses

### 404 Not Found

```json
{
  "detail": "Không tìm thấy khóa học với ID 999"
}
```

### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 3 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {
        "limit_value": 3
      }
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "detail": "Lỗi khi tạo khóa học: duplicate key value violates unique constraint"
}
```

## Best Practices

1. **Course Structure**: Plan your course structure before creating topics and lessons.

2. **Level Classification**: Use appropriate difficulty levels to help learners choose suitable courses.

3. **Pricing Strategy**: Set reasonable prices and consider offering free courses to attract learners.

4. **Publication Status**: Use `is_published` to control when courses become available to learners.

5. **Rich Metadata**: Provide comprehensive descriptions, requirements, and learning outcomes.

6. **Tags**: Use relevant tags to improve course discoverability.

## Complete Workflow Example

Here's a complete example of creating a course with topics and lessons:

```bash
# 1. Create a course
curl -X POST "http://localhost:8000/courses/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Programming for Beginners",
    "description": "Learn Python programming from scratch",
    "level": "Beginner",
    "duration": 600,
    "price": 0.0,
    "is_published": true,
    "tags": "python,programming,beginner"
  }'

# 2. Create topics for the course
curl -X POST "http://localhost:8000/topics/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Basics",
    "description": "Introduction to Python syntax and basic concepts",
    "course_id": 1,
    "order": 1
  }'

curl -X POST "http://localhost:8000/topics/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Control Structures",
    "description": "Learn about loops, conditionals, and control flow",
    "course_id": 1,
    "order": 2
  }'

# 3. Create lessons for the first topic
curl -X POST "http://localhost:8000/lessons/" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "external_id": "python-intro",
    "title": "Introduction to Python",
    "description": "What is Python and why learn it?",
    "topic_id": 1,
    "order": 1,
    "sections": [
      {
        "type": "text",
        "content": "Python is a high-level programming language...",
        "order": 1
      }
    ]
  }'

# 4. Get the complete course structure
curl -X GET "http://localhost:8000/courses/1" \
  -H "Authorization: Bearer your_token_here"

curl -X GET "http://localhost:8000/topics/course/1" \
  -H "Authorization: Bearer your_token_here"

curl -X GET "http://localhost:8000/topics/1/with-lessons" \
  -H "Authorization: Bearer your_token_here"
```

## Course Management Tips

1. **Start with a Plan**: Outline your course structure before creating content.

2. **Use Logical Ordering**: Arrange topics and lessons in a logical learning sequence.

3. **Provide Clear Prerequisites**: Help learners understand what they need to know beforehand.

4. **Set Realistic Expectations**: Clearly communicate what learners will achieve.

5. **Regular Updates**: Keep course content current and relevant.

6. **Quality Control**: Review and test all content before publishing.

7. **Engagement**: Include interactive elements and practical exercises.

8. **Feedback Loop**: Collect and incorporate learner feedback to improve courses.
