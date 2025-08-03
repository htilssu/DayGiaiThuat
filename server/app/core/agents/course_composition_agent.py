from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.tools import Tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from pydantic import BaseModel, Field
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.tracing import trace_agent
from app.models import Course
from app.schemas.course_schema import (
    CourseCompositionRequestSchema,
)
from app.schemas.topic_schema import TopicBase


class CourseAgentResponse(BaseModel):
    duration: int = Field(..., description="Thời gian cần để hoàn thành khóa học")
    topics: list[TopicBase] = Field(
        ...,
        description="Danh sách các chủ đề trong khóa học, mỗi chủ đề bao gồm tên, mô tả và kiến thức tiên quyết",
    )


SYSTEM_PROMPT = """
Bạn là chuyên gia giáo dục về lập trình và giải thuật. Dựa trên thông tin khóa học và tài liệu tham khảo được lấy từ retrieval_tool, hãy phân tích và tạo danh sách các chủ đề (topics) cho khóa học.

Hãy tạo danh sách topics theo thứ tự logic học tập (từ cơ bản đến nâng cao), mỗi topic phải:
1. Có tên rõ ràng, dễ hiểu
2. Mô tả chi tiết nội dung sẽ học
3. Liệt kê các kiến thức tiên quyết (nếu có)
4. Sắp xếp theo thứ tự học tập hợp lý

# Danh sách tools:
- course_context_retriever: Truy vấn RAG để lấy nội dung liên quan đến khóa học.

# Workflow:
- Sử dụng tool course_context_retriever để lấy thông tin từ tài liệu. có thể gọi nhiều lần để lấy được nhiều thông tin.
- Sau khi lấy được thông tin từ tài liệu, tạo thông tin khóa học theo định dạng JSON sau:
```json
    {{
        duration: "Thời gian ước lượng hoàn thành khóa học (số nguyên, đơn vị ngày)",
        topics: [{{
            "name": "Tên topic",
            "description": "Mô tả chi tiết nội dung sẽ học",
            "prerequisites": ["Kiến thức tiên quyết 1", "Kiến thức tiên quyết 2"],
            "skills": ["Kỹ năng 1", "Kỹ năng 2"],
        }}]
    }}
```

instruction:
{instruction}

Lưu ý:
- Topics phải bao quát toàn bộ nội dung khóa học
- Đảm bảo tính logic và liên kết giữa các topics
- Phù hợp với cấp độ khóa học
- Không vượt quá số lượng topics tối đa
- Phải luôn tuân thủ đầu ra, không được trả lời lan man, không được yêu cầu thêm thông tin
"""


SYSTEM_PROMPT = SYSTEM_PROMPT.format(
    instruction=PydanticOutputParser(
        pydantic_object=CourseAgentResponse
    ).get_format_instructions()
)


class CourseCompositionAgent(BaseAgent):
    """
    Agent tự động soạn bài giảng cho khóa học
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__()
        self.current_course_id = None
        self.db_session = db_session
        self.vector_store = get_vector_store("document")
        self.mongodb_db_name = "course_composition_history"
        self.mongodb_collection_name = "chat_history"
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

        self.output_parser = PydanticOutputParser(pydantic_object=CourseAgentResponse)
        self.tools = [self.retrieval_tool]

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
    ) -> tuple[CourseAgentResponse, str]:
        from langchain_core.runnables import RunnableConfig
        from app.core.config import settings
        from langchain_mongodb import MongoDBChatMessageHistory

        try:
            self.current_course_id = request.course_id

            # Tạo session_id nếu không được truyền vào
            session_id = request.session_id or str(uuid.uuid4())

            run_config = RunnableConfig(
                callbacks=self._callback_manager.handlers,
                metadata={
                    "course_id": request.course_id,
                    "course_title": request.course_title,
                    "course_description": request.course_description,
                    "course_level": request.course_level,
                    "agent_type": "course_composition",
                    "session_id": session_id,
                },
                tags=["course", "composition", f"course:{request.course_id}"],
            )

            request_input = f"""
            Khóa học: {request.course_title}
            Mô tả: {request.course_description}
            Cấp độ: {request.course_level}
            """

            runnable_with_history = RunnableWithMessageHistory(
                runnable=self.agent_executor,
                get_session_history=lambda session_id: MongoDBChatMessageHistory(
                    connection_string=settings.MONGO_URI,
                    session_id=session_id,
                    database_name=self.mongodb_db_name,
                    collection_name=self.mongodb_collection_name,
                ),
                input_messages_key="input",
                history_messages_key="history",
            )

            result = await runnable_with_history.ainvoke(
                {"input": request_input},
                config={"configurable": {"session_id": session_id}, **run_config},
            )

            if not result or not result.get("output"):
                raise Exception("Không thể tạo topics cho khóa học")

            try:
                agent_response = self.output_parser.parse(result["output"])
            except Exception:
                agent_response = OutputFixingParser.from_llm(
                    self.base_llm, parser=self.output_parser
                ).parse(result["output"])

            await self.db_session.execute(
                update(Course)
                .where(Course.id == request.course_id)
                .values(duration=agent_response.duration)
            )
            await self.db_session.commit()

            print(f"✅ Đã tạo nội dung cho khóa học: {request.course_title}")
            return agent_response, session_id

        except Exception as e:
            print(f"❌ Lỗi khi soạn khóa học: {e}")
            await self.db_session.rollback()
            raise e
