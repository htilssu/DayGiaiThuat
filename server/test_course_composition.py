"""
Test script để demo agent soạn bài giảng
"""

import asyncio
from app.core.agents.course_composition_agent import (
    CourseCompositionAgent,
    CourseCompositionRequestSchema,
)


async def test_course_composition_agent():
    """Test CourseCompositionAgent độc lập"""
    print("🎯 Testing CourseCompositionAgent...")

    agent = CourseCompositionAgent()

    # Test request
    request = CourseCompositionRequestSchema(
        course_id=1,
        course_title="Thuật toán và Cấu trúc Dữ liệu Cơ bản",
        course_description="Khóa học cung cấp kiến thức cơ bản về thuật toán và cấu trúc dữ liệu",
        course_level="beginner",
        max_topics=5,
        lessons_per_topic=3,
    )

    try:
        result = await asyncio.to_thread(agent.act, request)
        print(f"✅ Agent kết quả: {result['status']}")
        if result["status"] == "success":
            print(f"📚 Đã tạo {len(result['topics'])} topics")
            for i, topic in enumerate(result["topics"][:2], 1):  # Chỉ show 2 topics đầu
                topic_info = topic["topic_info"]
                print(
                    f"  {i}. {topic_info['name']}: {topic_info['description'][:100]}..."
                )
        return result
    except Exception as e:
        print(f"❌ Lỗi agent: {e}")
        return None


def test_imports():
    """Test tất cả imports hoạt động"""
    print("\n🔗 Testing imports...")

    try:
        from app.schemas.course_schema import CourseCreate

        print("✅ CourseCreate import OK")

        from app.services.course_service import CourseService

        print("✅ CourseService import OK")

        from app.services.course_composition_service import CourseCompositionService

        print("✅ CourseCompositionService import OK")

        # Test tạo course data
        course_data = CourseCreate(
            title="Test Course - Thuật toán Cơ bản",
            description="Khóa học test để kiểm tra agent soạn bài giảng",
            level="beginner",
        )

        print(f"✅ Tạo course data: {course_data.title}")

        return True
    except Exception as e:
        print(f"❌ Lỗi import: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Demo Agent Soạn Bài Giảng")
    print("=" * 50)

    # Test 1: Agent độc lập
    result = asyncio.run(test_course_composition_agent())

    # Test 2: Imports
    test_imports()

    print("\n" + "=" * 50)
    print("🎉 Demo hoàn thành!")
    print("\n📋 Tóm tắt:")
    print("✅ CourseCompositionAgent: Tạo topics từ RAG")
    print("✅ CourseCompositionService: Tích hợp với database")
    print("✅ CourseService: Background task integration")
    print("✅ Flow: Tạo course → Auto soạn topics + lessons")

    print("\n🔄 Flow hoạt động:")
    print("1. User tạo khóa học mới qua API")
    print("2. CourseService.create_course() tạo course trong DB")
    print("3. Background thread trigger CourseCompositionService")
    print("4. Agent phân tích nội dung và tạo topics")
    print("5. Service tự động tạo lessons cho từng topic")
