import asyncio
import uuid
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.agents.lesson_generating_agent import LessonGeneratingAgent
from app.database.database import get_independent_db_session
from app.models import Topic, Lesson
from app.models.lesson_model import LessonSection
from app.services.base_generate_service import BaseGenerateService
from app.utils.model_utils import pydantic_to_sqlalchemy_scalar


class LessonGenerateService(BaseGenerateService[List[Lesson]]):

    async def generate(self, topic: Topic, session_id: str) -> List[Lesson]:
        lesson_generate_agent = LessonGeneratingAgent()
        created_lesson_schema = await lesson_generate_agent.act(
            topic=topic, session_id=session_id
        )
        lesson_list = []
        for lesson_item in created_lesson_schema:
            lesson_model = pydantic_to_sqlalchemy_scalar(lesson_item, Lesson)
            lesson_model.topic_id = topic.id
            section = []
            for section_item in lesson_item.sections:
                section_model = pydantic_to_sqlalchemy_scalar(
                    section_item, LessonSection
                )
                section.append(section_model)
            lesson_model.sections = section
            # Không tạo exercises ở đây nữa, exercises sẽ được tạo bởi background task
            # thông qua service
            lesson_list.append(lesson_model)

        return lesson_list

    async def _create_exercises_for_lessons(
        self, lessons: Iterable[Lesson], topic_id: int, session_id: str
    ):
        """Tạo exercises cho các section có type 'exercise' trong lessons"""
        import json

        for lesson in lessons:
            lesson_content = ""
            exercise_sections = []

            for section in lesson.sections:
                lesson_content += f"\n{section.content}\n"
                if section.type == "exercise":
                    exercise_sections.append(section)

            # Tạo exercise cho mỗi section exercise
            for exercise_section in exercise_sections:
                try:
                    # Tạo requirement data với section ID thực sự
                    requirement_data = {
                        "lesson_id": lesson.id,
                        "section_id": exercise_section.id,  # ID thực sự từ DB
                        "topic_id": topic_id,
                        "difficulty": "Beginner",  # Có thể điều chỉnh logic để xác định difficulty
                        "session_id": session_id,
                        "lesson_content": lesson_content.strip(),
                    }

                    # Gọi trực tiếp function create_exercise_for_lesson
                    await self._call_create_exercise_function(
                        json.dumps(requirement_data)
                    )

                except Exception as e:
                    print(
                        f"Lỗi khi tạo exercise cho section {exercise_section.id}: {str(e)}"
                    )

    async def _call_create_exercise_function(self, user_requirement: str):
        """Gọi function tạo exercise trực tiếp"""
        try:
            from app.core.agents.exercise_agent import get_exercise_agent
            from app.database.database import get_independent_db_session
            import json

            # Parse user_requirement để lấy thông tin cần thiết
            requirement_data = json.loads(user_requirement)

            lesson_id = requirement_data.get("lesson_id")
            topic_id = requirement_data.get("topic_id")
            section_id = requirement_data.get("section_id")  # ID của section exercise
            difficulty = requirement_data.get("difficulty", "Beginner")
            session_id = requirement_data.get("session_id", "")
            lesson_content = requirement_data.get("lesson_content", "")

            if not all([lesson_id, topic_id, section_id, session_id]):
                print("Thiếu thông tin cần thiết để tạo bài tập")
                return

            # Sử dụng independent db session cho background task
            async with get_independent_db_session() as db:
                exercise_agent = get_exercise_agent()

                # Tạo enhanced user requirement cho exercise agent
                enhanced_requirement = f"""
                Tạo bài tập luyện tập cho lesson section với nội dung:
                {lesson_content}
                                
                Bài tập cần:
                - Phù hợp với nội dung lesson vừa học
                - Giúp học viên luyện tập và củng cố kiến thức
                - Độ khó: {difficulty}
                - Xác định loại bài tập phù hợp:
                  + Nếu lesson tập trung vào lý thuyết, khái niệm → executable=false (bài tập giải thích, phân tích)
                  + Nếu lesson có thuật toán, code example → executable=true (bài tập viết code)
                  + Nếu lesson về cấu trúc dữ liệu cơ bản → executable=true (bài tập implement)
                  + Nếu lesson về giới thiệu khái niệm → executable=false (bài tập lý thuyết)
                """

                lesson_info = {
                    "content": lesson_content,
                    "requirement": enhanced_requirement,
                }

                exercise_detail = await exercise_agent.act(
                    session_id=session_id,
                    topic=f"lesson_practice_{topic_id}",
                    difficulty=difficulty,
                    lesson=lesson_info,
                )

                # Lưu exercise vào database
                from app.models.exercise_model import (
                    Exercise as ExerciseModel,
                )
                from app.models.exercise_test_case_model import (
                    ExerciseTestCase,
                )

                exercise_model = ExerciseModel.exercise_from_schema(exercise_detail)
                db.add(exercise_model)
                await db.commit()
                await db.refresh(exercise_model)

                for testc in exercise_detail.case:
                    test_case = ExerciseTestCase(
                        exercise_id=exercise_model.id,
                        input_data=testc.input_data,
                        output_data=testc.output_data,
                        explain=testc.explain,
                    )
                    db.add(test_case)

                await db.commit()

                # Gán exercise_id cho lesson section
                from app.models.lesson_model import LessonSection

                section = await db.get(LessonSection, section_id)
                if section:
                    section.exercise_id = exercise_model.id
                    await db.commit()
                    print(
                        f"Đã gán exercise {exercise_model.id} cho section {section_id}"
                    )

                print(f"Đã tạo thành công bài tập luyện tập: {exercise_model.title}")

        except Exception as create_error:
            print(f"Lỗi khi tạo bài tập: {str(create_error)}")

    async def generate_all_by_topic(self, topic_list: List[Topic]):
        async def process_topic(topic):
            try:
                session_id = uuid.uuid4().hex
                lesson = await self.generate(topic=topic, session_id=session_id)

                for lesson_item in lesson:
                    lesson_item.topic_id = topic.id

                async with get_independent_db_session() as db:
                    db.add_all(lesson)
                    await db.commit()

                    result = await db.execute(
                        select(Lesson)
                        .where(Lesson.topic_id == topic.id)
                        .options(selectinload(Lesson.sections))
                    )
                    lessons = result.scalars().all()

                    await self._create_exercises_for_lessons(
                        lessons, topic.id, session_id
                    )

                    return True
            except Exception as err:
                print(f"Error topic {topic.id}: {err}")
                return False

        tasks = [process_topic(topic) for topic in topic_list]
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        print(f"Completed: {success_count}/{len(topic_list)}")
