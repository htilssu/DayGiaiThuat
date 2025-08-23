import asyncio
import uuid
from typing import List

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
        self, lesson_ids: List[int], topic_id: int, session_id: str
    ):
        """Tạo exercises cho các section có type 'exercise' trong lessons"""
        import json
        from app.models.lesson_model import Lesson, LessonSection
        from sqlalchemy import select

        for lesson_id in lesson_ids:
            # Sử dụng independent db session để lấy thông tin của lesson và sections
            async with get_independent_db_session() as db:
                # Lấy lesson
                lesson_query = select(Lesson).where(Lesson.id == lesson_id)
                lesson_result = await db.execute(lesson_query)
                lesson = lesson_result.scalar_one_or_none()
                
                if not lesson:
                    print(f"Không tìm thấy lesson với ID {lesson_id}")
                    continue
                
                # Lấy tất cả section của lesson
                sections_query = select(LessonSection).where(LessonSection.lesson_id == lesson_id)
                sections_result = await db.execute(sections_query)
                sections = sections_result.scalars().all()
                
                if not sections:
                    print(f"Không tìm thấy section nào cho lesson {lesson_id}")
                    continue
                
                # Tạo lesson content từ tất cả sections
                lesson_content = ""
                exercise_sections = []
                
                for section in sections:
                    lesson_content += f"\n{section.content}\n"
                    if section.type == "exercise":
                        exercise_sections.append(section)
            
            # Tạo exercise cho mỗi section exercise
            for exercise_section in exercise_sections:
                try:
                    # Tạo requirement data với section ID
                    requirement_data = {
                        "lesson_id": lesson_id,
                        "section_id": exercise_section.id,
                        "topic_id": topic_id,
                        "difficulty": "Beginner",
                        "session_id": session_id,
                        "lesson_content": lesson_content.strip(),
                    }

                    # Gọi trực tiếp function create_exercise_for_lesson - trong một context riêng biệt
                    try:
                        await self._call_create_exercise_function(
                            json.dumps(requirement_data)
                        )
                    except Exception as ex:
                        print(f"Lỗi khi tạo exercise cho section {exercise_section.id} trong context riêng: {str(ex)}")

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

            # Tạo một đối tượng exercise agent trước khi bắt đầu DB session
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

            # Override lesson trong kwargs để truyền thông tin lesson content
            lesson_info = {
                "content": lesson_content,
                "requirement": enhanced_requirement,
            }

            # Gọi exercise agent với thông tin bổ sung
            exercise_detail = await exercise_agent.act(
                session_id=session_id,
                topic=f"lesson_practice_{topic_id}",
                difficulty=difficulty,
                lesson=lesson_info,
            )

            # Sử dụng một independent db session mới cho việc lưu exercise
            # Điều này giúp tránh lỗi greenlet_spawn
            async with get_independent_db_session() as db:
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

                # Tạo test cases riêng biệt sau khi có exercise_id
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
                from sqlalchemy import select
                
                # Truy vấn để kiểm tra section tồn tại
                section_query = select(LessonSection).where(LessonSection.id == section_id)
                section_result = await db.execute(section_query)
                section = section_result.scalar_one_or_none()
                
                if section:
                    # Cập nhật section với exercise_id
                    section.exercise_id = exercise_model.id
                    await db.commit()
                    print(
                        f"Đã gán exercise {exercise_model.id} cho section {section_id}"
                    )
                else:
                    print(f"Không tìm thấy section với ID {section_id}")

                print(f"Đã tạo thành công bài tập luyện tập: {exercise_model.title}")

        except Exception as create_error:
            print(f"Lỗi khi tạo bài tập: {str(create_error)}")

    async def generate_all_by_topic(self, topic_list: List[Topic]):
        async def process_topic(topic):
            try:
                session_id = uuid.uuid4().hex
                lesson = await self.generate(topic=topic, session_id=session_id)

                lesson_ids = []  # Chỉ lưu trữ ID của lessons
                
                # Sử dụng một DB session độc lập cho mỗi topic
                async with get_independent_db_session() as db:
                    # Lưu lessons vào DB và lấy ID
                    for lesson_item in lesson:
                        lesson_item.topic_id = topic.id
                    
                    db.add_all(lesson)
                    await db.commit()

                    # Lấy IDs của lessons
                    for lesson_item in lesson:
                        await db.refresh(lesson_item)
                        lesson_ids.append(lesson_item.id)
                
                # Tạo một db session mới cho tác vụ tạo exercises
                # Truyền vào danh sách ID thay vì object
                await self._create_exercises_for_lessons(
                    lesson_ids, topic.id, session_id
                )

                return True
            except Exception as err:
                print(f"Error topic {topic.id}: {err}")
                return False

        tasks = [process_topic(topic) for topic in topic_list]
        results = await asyncio.gather(*tasks)

        success_count = sum(results)
        print(f"Completed: {success_count}/{len(topic_list)}")
