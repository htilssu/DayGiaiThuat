from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.schemas.course_schema import (
    CourseCompositionRequestSchema,
    CourseCompositionResponseSchema,
    TopicResponse,
)
from app.core.agents.lesson_generating_agent import LessonGeneratingAgent
from app.models.topic_model import Topic
from app.services.lesson_service import LessonService
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.tools import Tool
from app.core.tracing import trace_agent
import json
import uuid


SYSTEM_PROMPT = """
            Bạn là chuyên gia giáo dục về lập trình và giải thuật. Dựa trên thông tin khóa học và tài liệu tham khảo được lấy từ retrieval_tool, hãy phân tích và tạo danh sách các chủ đề (topics) cho khóa học.

            Hãy tạo danh sách topics theo thứ tự logic học tập (từ cơ bản đến nâng cao), mỗi topic phải:
            1. Có tên rõ ràng, dễ hiểu
            2. Mô tả chi tiết nội dung sẽ học
            3. Liệt kê các kiến thức tiên quyết (nếu có)
            4. Sắp xếp theo thứ tự học tập hợp lý
            # Danh sách tools:
            - course_context_retriever: Truy vấn RAG để lấy nội dung liên quan đến khóa học.
            - save_topics_to_db: Lưu danh sách các topic đã được tạo vào cơ sở dữ liệu. đối số là json array string của danh sách topic bắt buộc phải có dạng:
                ```json
                    [
                        {
                            "name": "Tên topic",
                            "description": "Mô tả chi tiết topic",
                            "prerequisites": ["Kiến thức tiên quyết 1", "Kiến thức tiên quyết 2"],
                            "order": 1
                        }
                    ]
                ```

            # Workflow:
            - Sử dụng tool course_context_retriever để lấy thông tin từ tài liệu. có thể gọi nhiều lần để lấy được nhiều thông tin.
            - Sau khi lấy được thông tin từ tài liệu, tạo 1 danh sách topic theo định dạng sau:
                ```json
                    [
                        {
                            "name": "Tên topic",
                            "description": "Mô tả chi tiết topic",
                            "prerequisites": ["Kiến thức tiên quyết 1", "Kiến thức tiên quyết 2"],
                            "order": 1
                        }
                    ]
                ```
                và gọi tool save_topics_to_db để lưu topic vào cơ sở dữ liệu.

            Lưu ý:
            - Topics phải bao quát toàn bộ nội dung khóa học
            - Đảm bảo tính logic và liên kết giữa các topics
            - Phù hợp với cấp độ khóa học
            - Không vượt quá số lượng topics tối đa
            - Phải luôn tuân thủ đầu ra, không được trả lời lan man, không được yêu cầu thêm thông tin
            """


class CourseCompositionAgent(BaseAgent):
    """
    Agent tự động soạn bài giảng cho khóa học
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__()
        self.db_session = db_session
        self.vector_store = get_vector_store("document")
        self._setup_tools()
        self._init_agent()

    def _setup_tools(self):
        """Khởi tạo các tools cho agent"""
        document_retriever = get_vector_store("document").as_retriever()
        self.retrieval_tool = Tool(
            name="course_context_retriever",
            func=document_retriever.invoke,
            coroutine=document_retriever.ainvoke,
            description="Truy vấn RAG để lấy nội dung liên quan đến khóa học.",
        )

        self.store_topic_tool = Tool(
            name="save_topics_to_db",
            func=self._store_topic,
            coroutine=self._astore_topic,
            description="Lưu danh sách các topic đã được tạo vào cơ sở dữ liệu.",
        )

        # Comment out output fixing parser for now as output_parser is not defined
        # self.output_fixing_parser = OutputFixingParser.from_llm(
        #     self.base_llm, self.output_parser
        # )

        # self.output_fixing_parser_tool = Tool(
        #     "OutputFixingParser",
        #     func=self.output_fixing_parser.invoke,
        #     coroutine=self.output_fixing_parser.ainvoke,
        #     description="Sửa lỗi trong response từ LLM.",
        # )
        self.tools = [self.retrieval_tool, self.store_topic_tool]

    def _store_topic(self, t: str):
        """Lưu topic vào cơ sở dữ liệu (đồng bộ wrapper)"""
        import asyncio

        # Tạo một event loop mới nếu không có sẵn
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Chạy phương thức bất đồng bộ trong event loop
        return loop.run_until_complete(self._astore_topic(t))

    async def _astore_topic(self, t: str):
        """Lưu topic vào cơ sở dữ liệu (bất đồng bộ)"""
        if not self.db_session:
            raise ValueError("db_session chưa được khởi tạo.")
        try:
            topics = json.loads(t)
            for topic_data in topics:
                # topic_data đã là dictionary nên không cần gọi .dict()
                # Thêm course_id nếu có trong request
                if hasattr(self, "current_course_id") and self.current_course_id:
                    topic_data["course_id"] = self.current_course_id
                new_topic = Topic(**topic_data)
                self.db_session.add(new_topic)
            await self.db_session.commit()
        except Exception as e:
            print(f"Lỗi khi lưu topic vào cơ sở dữ liệu: {e}")
            await self.db_session.rollback()
            return False
        return True

    async def _get_topics_by_course_id(self, course_id: int) -> list[Topic]:
        """Lấy danh sách topics theo course_id từ database"""
        from sqlalchemy import select
        from app.models.topic_model import Topic

        try:
            result = await self.db_session.execute(
                select(Topic).where(Topic.course_id == course_id)
            )
            return [topic for topic in result.scalars().all()]
        except Exception as e:
            print(f"Lỗi khi lấy topics từ database: {e}")
            return []

    def _init_agent(self):
        """Khởi tạo agent với lazy import"""
        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import (
            ChatPromptTemplate,
            MessagesPlaceholder,
            HumanMessagePromptTemplate,
        )
        from langchain.agents import AgentExecutor, create_tool_calling_agent

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.agent = create_tool_calling_agent(
            self.base_llm,
            self.tools,
            self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            max_iterations=40,
            tools=self.tools,
            verbose=True,
        )

    @trace_agent(project_name="default", tags=["course", "composition"])
    async def act(
        self, request: CourseCompositionRequestSchema
    ) -> CourseCompositionResponseSchema:
        """Tự động soạn toàn bộ khóa học: tạo topics và lessons"""
        from langchain_core.runnables import RunnableConfig

        errors = []
        try:
            self.current_course_id = request.course_id

            run_config = RunnableConfig(
                callbacks=self._callback_manager.handlers,
                metadata={
                    "course_id": request.course_id,
                    "course_title": request.course_title,
                    "course_description": request.course_description,
                    "course_level": request.course_level,
                    "agent_type": "course_composition",
                },
                tags=["course", "composition", f"course:{request.course_id}"],
            )

            input = f"""
            Khóa học: {request.course_title}
            Mô tả: {request.course_description}
            Cấp độ: {request.course_level}
            """
            result = await self.agent_executor.ainvoke(
                {"input": input}, config=run_config
            )

            if not result or not result.get("output"):
                errors.append("Không thể tạo topics cho khóa học")
                return CourseCompositionResponseSchema(
                    course_id=request.course_id,
                    topics=[],
                    status="failed",
                    errors=errors,
                )

            topics_from_db = await self._get_topics_by_course_id(request.course_id)

            # Khởi tạo LessonService
            from app.services.topic_service import TopicService

            # Tạo topic_service trực tiếp vì không thể dùng Depends
            topic_service = TopicService(self.db_session)
            lesson_service = LessonService(self.db_session, topic_service)

            for topic in topics_from_db:
                session_id = str(uuid.uuid4())

                lesson_data = await LessonGeneratingAgent().act(
                    topic_name=topic.name,
                    lesson_title=f"Bài giảng {topic.name}",
                    lesson_description=topic.description,
                    difficulty_level=request.course_level,
                    lesson_type="video",
                    max_sections=5,
                    session_id=session_id,
                )

                # Lưu lesson vào database
                for lesson in lesson_data:
                    lesson.topic_id = topic.id
                    await lesson_service.create_lesson(lesson)

            # Chuyển đổi topics_from_db thành danh sách TopicResponse từ course_schema
            from typing import List

            topic_responses: List[TopicResponse] = []
            for topic in topics_from_db:
                topic_responses.append(
                    TopicResponse(
                        id=topic.id,
                        name=topic.name,
                        description=topic.description,
                        prerequisites=topic.prerequisites,
                        external_id=topic.external_id,
                        course_id=(
                            topic.course_id
                            if topic.course_id is not None
                            else request.course_id
                        ),
                    )
                )

            return CourseCompositionResponseSchema(
                course_id=request.course_id,
                topics=topic_responses,
                status="success",
                errors=errors,
            )

        except Exception as e:
            print(f"❌ Lỗi khi soạn khóa học: {e}")
            errors.append(f"Lỗi hệ thống: {str(e)}")
            return CourseCompositionResponseSchema(
                course_id=request.course_id,
                topics=[],
                status="failed",
                errors=errors,
            )
