"""
Demo cho Cách 2: ORM + Response Schema dạng Nested

Minh họa cách sử dụng NestedCourseProgressService để query và trả về
course với topics, lessons và progress nested.
"""


def demo_nested_response_structure():
    """
    Demo cấu trúc response của cách 2
    """
    print("🎯 Cách 2: ORM + Response Schema dạng Nested")
    print("=" * 60)

    # Ưu điểm
    print("\n✅ Ưu điểm:")
    print("• Query tất cả topics với lessons nested một lần")
    print("• Query progress map riêng biệt")
    print("• Map progress status bằng Python")
    print("• Tránh join phức tạp")
    print("• Performance tốt với khóa học nhỏ/vừa")
    print("• Response nested đẹp, dễ sử dụng")

    # Cách hoạt động
    print("\n🔄 Cách hoạt động:")
    print("1. Query UserCourse với course info")
    print("2. Query tất cả topics với lessons (eager loading)")
    print("3. Query progress map: lesson_id -> {status, last_viewed_at, completed_at}")
    print("4. Map progress status cho từng lesson bằng Python")

    # Sample response
    print("\n📋 Sample Response:")
    sample_response = {
        "user_course_id": 1,
        "course_id": 101,
        "course_title": "React Fundamentals",
        "course_description": "Learn React from scratch",
        "topics": [
            {
                "id": 1,
                "name": "Introduction to React",
                "description": "Basic concepts and setup",
                "order": 1,
                "lessons": [
                    {
                        "id": 101,
                        "external_id": "1",
                        "title": "What is React?",
                        "description": "Overview of React framework",
                        "order": 1,
                        "status": "completed",
                        "last_viewed_at": "2025-07-14T10:30:00Z",
                        "completed_at": "2025-07-14T11:00:00Z",
                        "completion_percentage": 100.0,
                    },
                    {
                        "id": 102,
                        "external_id": "2",
                        "title": "Setting up Development Environment",
                        "description": "Install Node.js, npm, and create-react-app",
                        "order": 2,
                        "status": "in_progress",
                        "last_viewed_at": "2025-07-14T12:00:00Z",
                        "completed_at": None,
                        "completion_percentage": 50.0,
                    },
                    {
                        "id": 103,
                        "external_id": "3",
                        "title": "Your First Component",
                        "description": "Create and render your first React component",
                        "order": 3,
                        "status": "not_started",
                        "last_viewed_at": None,
                        "completed_at": None,
                        "completion_percentage": 0.0,
                    },
                ],
                "topic_completion_percentage": 50.0,  # 1/3 completed, 1/3 in progress
                "completed_lessons": 1,
                "total_lessons": 3,
            },
            {
                "id": 2,
                "name": "Components and Props",
                "description": "Deep dive into React components",
                "order": 2,
                "lessons": [
                    {
                        "id": 201,
                        "external_id": "4",
                        "title": "Function Components",
                        "description": "Creating components with functions",
                        "order": 1,
                        "status": "not_started",
                        "last_viewed_at": None,
                        "completed_at": None,
                        "completion_percentage": 0.0,
                    },
                    {
                        "id": 202,
                        "external_id": "5",
                        "title": "Props and Data Flow",
                        "description": "Passing data between components",
                        "order": 2,
                        "status": "not_started",
                        "last_viewed_at": None,
                        "completed_at": None,
                        "completion_percentage": 0.0,
                    },
                ],
                "topic_completion_percentage": 0.0,
                "completed_lessons": 0,
                "total_lessons": 2,
            },
        ],
        "total_topics": 2,
        "total_lessons": 5,
        "completed_lessons": 1,
        "in_progress_lessons": 1,
        "not_started_lessons": 3,
        "overall_completion_percentage": 20.0,  # 1/5 completed
        "current_topic_id": 1,
        "current_lesson_id": 102,
        "last_activity_at": "2025-07-14T12:00:00Z",
    }

    print(f"📊 Course: {sample_response['course_title']}")
    print(f"📈 Overall Progress: {sample_response['overall_completion_percentage']}%")
    print(f"📚 Topics: {sample_response['total_topics']}")
    print(f"📖 Total Lessons: {sample_response['total_lessons']}")
    print(f"✅ Completed: {sample_response['completed_lessons']}")
    print(f"🔄 In Progress: {sample_response['in_progress_lessons']}")
    print(f"⏸️  Not Started: {sample_response['not_started_lessons']}")

    # Detail breakdown
    print("\n📋 Topic Breakdown:")
    for topic in sample_response["topics"]:
        print(f"  🎯 {topic['name']} ({topic['topic_completion_percentage']}%)")
        for lesson in topic["lessons"]:
            status_emoji = {"completed": "✅", "in_progress": "🔄", "not_started": "⏸️"}
            emoji = status_emoji.get(lesson["status"], "❓")
            print(f"    {emoji} {lesson['title']} ({lesson['completion_percentage']}%)")


def demo_api_usage():
    """
    Demo cách sử dụng API endpoints
    """
    print("\n🚀 API Usage Examples:")
    print("=" * 40)

    print("\n1️⃣ Get course with nested progress:")
    print("GET /nested/course/1")
    print("→ Returns full course structure with progress")

    print("\n2️⃣ Get single topic with progress:")
    print("GET /nested/course/1/topic/1")
    print("→ Returns one topic with lessons and progress")

    print("\n3️⃣ Get progress map only:")
    print("GET /nested/course/1/progress-map")
    print("→ Returns lesson_id -> progress mapping")

    sample_progress_map = {
        "user_course_id": 1,
        "progress_map": {
            "101": {
                "status": "completed",
                "last_viewed_at": "2025-07-14T10:30:00Z",
                "completed_at": "2025-07-14T11:00:00Z",
                "completion_percentage": 100.0,
            },
            "102": {
                "status": "in_progress",
                "last_viewed_at": "2025-07-14T12:00:00Z",
                "completed_at": None,
                "completion_percentage": 50.0,
            },
            "103": {
                "status": "not_started",
                "last_viewed_at": None,
                "completed_at": None,
                "completion_percentage": 0.0,
            },
        },
        "summary": {
            "total_lessons": 3,
            "completed_lessons": 1,
            "in_progress_lessons": 1,
            "not_started_lessons": 1,
            "completion_percentage": 33.33,
        },
    }

    print("\n📊 Progress Map Response:")
    print(f"Total lessons: {sample_progress_map['summary']['total_lessons']}")
    print(f"Completion: {sample_progress_map['summary']['completion_percentage']}%")
    print("Progress mapping:")
    for lesson_id, progress in sample_progress_map["progress_map"].items():
        print(
            f"  Lesson {lesson_id}: {progress['status']} ({progress['completion_percentage']}%)"
        )


def demo_performance_considerations():
    """
    Demo các cân nhắc về performance
    """
    print("\n⚡ Performance Considerations:")
    print("=" * 40)

    print("\n✅ Tối ưu:")
    print("• Sử dụng selectinload để eager load lessons")
    print("• Query progress map riêng biệt, tránh N+1")
    print("• Map progress bằng Python thay vì SQL JOIN")
    print("• Có thể cache progress map")
    print("• Response nhỏ gọn, dễ serialize")

    print("\n🎯 Best for:")
    print("• Khóa học nhỏ/vừa (< 100 lessons)")
    print("• Frontend cần structure nested")
    print("• Cần hiển thị progress theo topic")
    print("• Muốn tránh JOIN phức tạp")

    print("\n⚠️  Cân nhắc:")
    print("• Với khóa học lớn, có thể cần pagination")
    print("• Progress map có thể lớn với nhiều lesson")
    print("• Cần optimize caching cho performance tốt hơn")


def demo_frontend_integration():
    """
    Demo cách frontend có thể sử dụng
    """
    print("\n🎨 Frontend Integration:")
    print("=" * 40)

    print("\n📱 React/Vue.js Example:")
    frontend_code = """
// Fetch course with nested progress
const response = await fetch('/nested/course/1');
const courseData = await response.json();

// Easy to render nested structure
courseData.topics.forEach(topic => {
  console.log(`Topic: ${topic.name} (${topic.topic_completion_percentage}%)`);
  
  topic.lessons.forEach(lesson => {
    console.log(`  Lesson: ${lesson.title} - ${lesson.status}`);
    
    // Update UI based on status
    if (lesson.status === 'completed') {
      showCheckmark(lesson.id);
    } else if (lesson.status === 'in_progress') {
      showProgressIndicator(lesson.id, lesson.completion_percentage);
    }
  });
});

// Overall progress
updateProgressBar(courseData.overall_completion_percentage);
showCurrentLesson(courseData.current_topic_id, courseData.current_lesson_id);
"""
    print(frontend_code)

    print("\n🎯 Ưu điểm cho Frontend:")
    print("• Structure sẵn, không cần map thêm")
    print("• Progress data đi kèm với lesson info")
    print("• Dễ render UI nested (accordion, sidebar)")
    print("• Có summary stats để hiển thị tổng quan")


if __name__ == "__main__":
    print("🎯 Demo: Cách 2 - ORM + Response Schema dạng Nested")
    print("🚀 Triển khai UserCourseProgress với Nested Response")
    print("=" * 70)

    demo_nested_response_structure()
    demo_api_usage()
    demo_performance_considerations()
    demo_frontend_integration()

    print("\n" + "=" * 70)
    print("✅ Demo completed! Check the router and service for implementation.")
    print("📂 Files created:")
    print("  • app/schemas/nested_course_progress_schema.py")
    print("  • app/services/nested_course_progress_service.py")
    print("  • app/routers/nested_course_progress_router.py")
    print("  • app/examples/nested_course_progress_demo.py")
    print("\n🔗 Add router to main.py:")
    print("  from app.routers import nested_course_progress_router")
    print(
        "  app.include_router(nested_course_progress_router.router, prefix='/api/v1', tags=['Nested Course Progress'])"
    )
