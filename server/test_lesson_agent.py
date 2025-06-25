#!/usr/bin/env python3
"""
Test script for the Lesson Generating Agent.
This script demonstrates how to use the RAG AI agent to generate lesson content.
"""

import asyncio
from app.core.agents.lesson_generating_agent import LessonGeneratingAgent
from app.schemas.lesson_schema import GenerateLessonRequestSchema


async def test_lesson_generation():
    """Test the lesson generation functionality."""

    # Create the agent
    agent = LessonGeneratingAgent()

    # Create a test request
    request = GenerateLessonRequestSchema(
        topic_name="Thuật toán sắp xếp",
        lesson_title="Bubble Sort - Thuật toán sắp xếp nổi bọt",
        lesson_description="Học về thuật toán sắp xếp bubble sort, cách hoạt động và cách implement",
        difficulty_level="beginner",
        lesson_type="mixed",
        include_examples=True,
        include_exercises=True,
        max_sections=5
    )

    try:
        # Generate the lesson
        print("🔄 Generating lesson...")
        lesson = agent.act(request)

        print("✅ Lesson generated successfully!")
        print(f"📝 Title: {lesson.title}")
        print(f"📄 Description: {lesson.description}")
        print(f"🆔 External ID: {lesson.external_id}")
        print(f"📊 Number of sections: {len(lesson.sections)}")

        # Display sections
        for i, section in enumerate(lesson.sections, 1):
            print(f"\n--- Section {i} ---")
            print(f"Type: {section.type}")
            print(f"Order: {section.order}")
            print(f"Content: {section.content[:100]}...")

            if section.options:
                print(f"Options: {section.options}")
            if section.answer is not None:
                print(f"Answer: {section.answer}")
            if section.explanation:
                print(f"Explanation: {section.explanation}")

        return lesson

    except Exception as e:
        print(f"❌ Error generating lesson: {e}")
        return None


if __name__ == "__main__":
    print("🚀 Starting Lesson Generating Agent Test")
    print("=" * 50)

    # Run the test
    lesson = asyncio.run(test_lesson_generation())

    if lesson:
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
    else:
        print("\n" + "=" * 50)
        print("❌ Test failed!")
