# Cách 2: ORM + Response Schema dạng Nested

## Tổng quan

Cách 2 triển khai UserCourseProgress với approach "ORM + Response Schema dạng Nested". Phương pháp này query tất cả topics với lessons nested, sau đó map progress status bằng Python.

## Kiến trúc

### 🏗️ Components

1. **Schema Layer** (`nested_course_progress_schema.py`)
   - `LessonWithProgressSchema`: Lesson với progress info
   - `TopicWithProgressSchema`: Topic với lessons nested
   - `CourseWithNestedProgressSchema`: Course với full nested structure
   - `ProgressMapResponse`: Progress map cho optimization

2. **Service Layer** (`nested_course_progress_service.py`)
   - `NestedCourseProgressService`: Core business logic
   - Eager loading với `selectinload`
   - Progress mapping bằng Python

3. **Router Layer** (`nested_course_progress_router.py`)
   - `/nested/course/{user_course_id}`: Full nested response
   - `/nested/course/{user_course_id}/topic/{topic_id}`: Single topic
   - `/nested/course/{user_course_id}/progress-map`: Progress map only

## Cách hoạt động

### 📊 Query Strategy

```python
# Step 1: Query UserCourse với course info
user_course = await db.execute(
    select(UserCourse)
    .options(selectinload(UserCourse.course))
    .where(UserCourse.id == user_course_id)
)

# Step 2: Query tất cả topics với lessons nested
topics = await db.execute(
    select(Topic)
    .options(selectinload(Topic.lessons))
    .where(Topic.course_id == course_id)
    .order_by(Topic.order)
)

# Step 3: Query progress map
progress = await db.execute(
    select(UserCourseProgress.lesson_id, UserCourseProgress.status)
    .where(UserCourseProgress.user_course_id == user_course_id)
)
progress_map = {row.lesson_id: row.status for row in progress}

# Step 4: Map progress cho từng lesson
for topic in topics:
    for lesson in topic.lessons:
        lesson.status = progress_map.get(lesson.id, 'not_started')
```

### 🎯 Response Structure

```json
{
  "user_course_id": 1,
  "course_title": "React Fundamentals",
  "topics": [
    {
      "id": 1,
      "name": "Introduction",
      "lessons": [
        {
          "id": 101,
          "title": "Getting Started",
          "status": "completed",
          "completion_percentage": 100.0,
          "last_viewed_at": "2025-07-14T10:30:00Z",
          "completed_at": "2025-07-14T11:00:00Z"
        },
        {
          "id": 102,
          "title": "Components",
          "status": "in_progress",
          "completion_percentage": 50.0,
          "last_viewed_at": "2025-07-14T12:00:00Z"
        }
      ],
      "topic_completion_percentage": 75.0,
      "completed_lessons": 1,
      "total_lessons": 2
    }
  ],
  "overall_completion_percentage": 45.0,
  "current_topic_id": 1,
  "current_lesson_id": 102
}
```

## Ưu điểm

### ✅ Performance
- **Eager Loading**: Sử dụng `selectinload` tránh N+1 queries
- **Separate Progress Query**: Query progress map riêng biệt
- **Python Mapping**: Map progress bằng Python thay vì SQL JOIN
- **Cacheable**: Progress map có thể cache dễ dàng

### ✅ Developer Experience
- **Nested Structure**: Response có cấu trúc sẵn, dễ sử dụng
- **Type Safety**: Full Pydantic schemas với type hints
- **Readable Code**: Logic rõ ràng, dễ maintain
- **Testable**: Dễ mock và test

### ✅ Frontend Friendly
- **Ready-to-use**: Không cần map thêm ở frontend
- **Rich Data**: Progress info đi kèm với lesson data
- **Flexible**: Có thể request full nested hoặc chỉ progress map

## Use Cases

### 🎯 Best For

1. **Khóa học nhỏ/vừa** (< 100 lessons)
2. **Frontend cần nested structure** (accordion, sidebar)
3. **Hiển thị progress theo topic**
4. **Muốn tránh JOIN phức tạp**

### ⚠️ Considerations

1. **Large Courses**: Cần pagination cho khóa học lớn
2. **Memory Usage**: Progress map có thể lớn với nhiều lesson
3. **Caching Strategy**: Cần optimize caching cho performance tốt hơn

## API Endpoints

### 📡 Full Nested Response

```http
GET /api/v1/nested/course/{user_course_id}
```

**Response**: Full course với topics, lessons và progress nested

**Use Case**: Hiển thị trang overview khóa học

### 📡 Single Topic

```http
GET /api/v1/nested/course/{user_course_id}/topic/{topic_id}
```

**Response**: Một topic với lessons và progress

**Use Case**: Load từng topic riêng lẻ

### 📡 Progress Map Only

```http
GET /api/v1/nested/course/{user_course_id}/progress-map
```

**Response**: Chỉ progress mapping

**Use Case**: Frontend tự map, check nhanh progress

## Implementation Details

### 🔧 Core Service Method

```python
async def get_course_with_nested_progress(self, user_course_id: int):
    # 1. Query UserCourse
    user_course = await self._get_user_course(user_course_id)
    
    # 2. Query Topics với Lessons
    topics = await self._get_topics_with_lessons(user_course.course_id)
    
    # 3. Query Progress Map
    progress_map = await self._get_progress_map(user_course_id)
    
    # 4. Build Nested Response
    return self._build_nested_response(
        user_course, topics, progress_map
    )
```

### 🔧 Progress Mapping

```python
def _map_lesson_progress(self, lesson, progress_map):
    lesson_progress = progress_map.get(lesson.id, {
        "status": ProgressStatus.NOT_STARTED,
        "last_viewed_at": None,
        "completed_at": None
    })
    
    completion_percentage = {
        ProgressStatus.NOT_STARTED: 0.0,
        ProgressStatus.IN_PROGRESS: 50.0,
        ProgressStatus.COMPLETED: 100.0,
    }.get(lesson_progress["status"], 0.0)
    
    return LessonWithProgressSchema(
        id=lesson.id,
        title=lesson.title,
        status=lesson_progress["status"],
        completion_percentage=completion_percentage,
        # ... other fields
    )
```

## Testing

### 🧪 Test Coverage

- ✅ **Happy Path**: Course với progress thành công
- ✅ **Progress Map**: Test progress mapping logic
- ✅ **Error Handling**: User course not found
- ✅ **Edge Cases**: Empty progress, no lessons
- ✅ **Utility Functions**: Sorting, status mapping

### 🧪 Run Tests

```bash
pytest app/tests/test_nested_course_progress_service.py -v
```

## Frontend Integration

### 🎨 React Example

```javascript
// Fetch nested course data
const { data: courseData } = await fetch('/api/v1/nested/course/1');

// Render topics and lessons
courseData.topics.map(topic => (
  <TopicCard key={topic.id} topic={topic}>
    {topic.lessons.map(lesson => (
      <LessonItem 
        key={lesson.id}
        lesson={lesson}
        status={lesson.status}
        progress={lesson.completion_percentage}
      />
    ))}
  </TopicCard>
));

// Update overall progress
setOverallProgress(courseData.overall_completion_percentage);
```

### 🎨 Ưu điểm cho Frontend

- **No Additional Mapping**: Data structure sẵn sàng sử dụng
- **Rich Progress Info**: Có progress ở mọi level (lesson, topic, course)
- **Current Position**: Biết user đang ở lesson nào
- **Flexible Rendering**: Có thể render nested hoặc flat

## Performance Optimization

### ⚡ Caching Strategy

```python
# Cache progress map
@cache(ttl=300)  # 5 minutes
async def get_progress_map_cached(user_course_id: int):
    return await self.get_progress_map_only(user_course_id)

# Cache course structure
@cache(ttl=3600)  # 1 hour
async def get_course_structure_cached(course_id: int):
    return await self._get_topics_with_lessons(course_id)
```

### ⚡ Database Optimization

- **Indexes**: Trên `user_course_id`, `lesson_id` trong progress table
- **Eager Loading**: `selectinload(Topic.lessons)` 
- **Query Batching**: Combine related queries khi có thể

## Migration Path

Từ hệ thống cũ sang cách 2:

1. **Phase 1**: Deploy schema và service mới
2. **Phase 2**: Update frontend sử dụng nested endpoints
3. **Phase 3**: Deprecate old progress endpoints
4. **Phase 4**: Add caching và optimization

## So sánh với các cách khác

| Aspect | Cách 2 (Nested) | Cách 1 (Flat) | Cách 3 (JOIN) |
|--------|------------------|----------------|----------------|
| Query Performance | ✅ Good | ✅ Good | ⚠️ Complex JOIN |
| Response Size | ⚠️ Large | ✅ Small | ⚠️ Large |
| Frontend Ease | ✅ Easy | ⚠️ Need mapping | ✅ Easy |
| Scalability | ⚠️ Limited | ✅ Good | ⚠️ Limited |
| Caching | ✅ Easy | ✅ Easy | ⚠️ Hard |

## Kết luận

Cách 2 là lựa chọn tốt cho:
- ✅ **Mid-sized courses** với structure phức tạp
- ✅ **Frontend-heavy applications** cần data nested sẵn
- ✅ **Teams ưu tiên developer experience**
- ✅ **Use cases cần hiển thị progress theo topic**

Không phù hợp cho:
- ❌ **Very large courses** (>1000 lessons)
- ❌ **Mobile apps** với bandwidth limited
- ❌ **Simple progress tracking** không cần nested data
