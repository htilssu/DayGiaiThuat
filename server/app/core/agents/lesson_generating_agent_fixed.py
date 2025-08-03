import json
from typing import override

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.llm_model import create_new_creative_llm_model
from app.core.agents.components.document_store import get_vector_store
from app.core.config import settings
from app.core.tracing import trace_agent
from app.schemas.lesson_schema import CreateLessonSchema

SYSTEM_PROMPT_TEMPLATE = """
Bạn là một AI agent chuyên nghiệp, có nhiệm vụ tạo ra các bài giảng lập trình và giải thuật chất lượng cao.

QUAN TRỌNG: Bạn PHẢI làm theo đúng quy trình từng bước như sau và KHÔNG ĐƯỢC DỪNG CHO ĐẾN KHI HOÀN THÀNH:

1. **Nghiên cứu tài liệu:** Sử dụng `retriever_document_tool` để tìm kiếm và thu thập thông tin liên quan đến chủ đề được yêu cầu từ kho tài liệu (có thể gọi nhiều lần để truy vấn dữ liệu đầy đủ nhất).
2. **Tạo bài giảng:** Dựa trên thông tin đã thu thập, phác thảo bài giảng và sử dụng `generate_lesson_tool` để tạo bài giảng chi tiết,
đối số là miêu tả kịch bản học gồm nhiều lesson (một topic có nhiều lesson) có chắt lọc thông tin từ retriever_document_tool để đưa vào cho generate_lesson_tool. 1 đoạn văn bản.

LƯU Ý QUAN TRỌNG:
- BẠN PHẢI THỰC HIỆN TẤT CẢ CÁC BƯỚC TRÊN. KHÔNG ĐƯỢC BỎ QUA BƯỚC NÀO.
- Cho dù không đủ thông tin yêu cầu vẫn phải đi theo luồng của quy trình. KHÔNG ĐƯỢC YÊU CẦU BỔ SUNG THÊM THÔNG TIN.
- KHÔNG ĐƯỢC DỪNG CHO ĐẾN KHI CÓ KẾT QUẢ CUỐI CÙNG
- Đối số của `generate_lesson_tool` là miêu tả kịch bản học chi tiết có đưa dữ liệu lấy từ retriever_document_tool để tham chiếu,lesson này học gì, section này có những gì, bổ sung kiến thức nào, có thể có các câu hỏi, lời giải thích, lời giảng dạy như một người giáo viên
    ,dựa vào tài liệu đã thu thập. 1 đoạn văn bản string, không phải json.

"""

STRUCTURE_PROMPT_TEMPLATE = """Bạn là một chuyên gia thiết kế chương trình học. Hãy tạo cấu trúc cho nhiều bài giảng (lesson) dựa vào đầu vào.

Hướng dẫn về từng loại section:
- "teaching": Phần giảng dạy, truyền đạt kiến thức, có thể chứa giải thích, ví dụ, hướng dẫn
- "quiz": Phần câu hỏi trắc nghiệm để kiểm tra hiểu biết của học viên
- "text": Phần văn bản thuần túy
- "code": Phần code mẫu hoặc ví dụ lập trình
- "image": Phần hình ảnh minh họa

Đối với section loại "quiz":
- "options" phải là một object có các key là A, B, C, D (không bọc bằng dấu nháy).
- "answer" phải là một trong các giá trị: "A", "B", "C", "D"
- Phải có "explanation" để giải thích đáp án

Đối với các section khác (teaching, text, code, image):
- "options" phải là null
- "answer" phải là null  
- "explanation" phải là null

# QUAN TRỌNG:
- type của section phải là một trong các giá trị sau: "text", "code", "quiz", "teaching", "image".
- Khi kết thúc (không gọi tool nữa), hãy trả về một JSON có định dạng như sau:
{format_instructions}
"""


class LessonGeneratingAgent(BaseAgent):
    """
    Một AI agent sử dụng Langchain để tạo ra nội dung bài giảng.
    Agent này có khả năng sử dụng các tool để truy vấn kiến thức,
    tạo cấu trúc, soạn nội dung và đảm bảo định dạng đầu ra.
    """

    def __init__(
        self,
        mongodb_db_name: str = "chat_history",
        mongodb_collection_name: str = "lesson_chat_history",
    ):
        super().__init__()
        self.available_args = [
            "topic_name",
            "lesson_title",
            "lesson_description",
            "difficulty_level",
            "lesson_type",
            "max_sections",
            "session_id",
        ]
        self.mongodb_collection_name = mongodb_collection_name
        self.mongodb_db_name = mongodb_db_name

        self.retriever = get_vector_store("document").as_retriever(
            search_kwargs={"k": 5}
        )

        self._init_parsers_and_chains()
        self._init_tools()
        self._init_agent()

    def _init_parsers_and_chains(self):
        """Khởi tạo parsers và chains."""
        from langchain_core.output_parsers import PydanticOutputParser
        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import (
            ChatPromptTemplate,
            HumanMessagePromptTemplate,
        )

        from typing import List
        from pydantic import BaseModel

        class ListCreateLessonSchema(BaseModel):
            """
            Danh sách các bài giảng được tạo ra.
            """

            list_schema: List[CreateLessonSchema]

        self.structure_parser = PydanticOutputParser(
            pydantic_object=ListCreateLessonSchema
        )

        # Chain for generating lesson structure
        self.generate_structure_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=STRUCTURE_PROMPT_TEMPLATE.format(
                        format_instructions=self.structure_parser.get_format_instructions()
                    )
                ),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )
        self.generate_structure_chain = (
            self.generate_structure_prompt | create_new_creative_llm_model()
        )

        # Chain for generating section content
        self.generate_content_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="Bạn là một người viết nội dung giáo dục. Hãy soạn nội dung chi tiết cho phần này của bài giảng."
                ),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

    def _init_tools(self):
        """Khởi tạo tools."""
        from langchain.output_parsers import OutputFixingParser
        from langchain_core.tools import Tool

        self.retriever_document_tool = Tool(
            name="retriever_document_tool",
            func=self.retriever.invoke,
            coroutine=self.retriever.ainvoke,
            description="Truy xuất tài liệu và kiến thức từ kho vector để hỗ trợ việc tạo bài giảng. BẮT BUỘC phải sử dụng tool này đầu tiên để tìm hiểu về chủ đề.",
        )

        self.generate_lesson_structure_tool = Tool(
            name="generate_lesson_tool",
            func=lambda x: self.generate_structure_chain.invoke({"input": x}),
            coroutine=lambda x: self.generate_structure_chain.ainvoke({"input": x}),
            description="Tạo cấu trúc bài giảng (các phần, tiêu đề) dựa trên chủ đề và thông tin tham khảo. PHẢI sử dụng sau khi đã tìm hiểu tài liệu.",
        )

        self.output_fixing_parser = OutputFixingParser.from_llm(
            self.base_llm, self.structure_parser
        )

        self.output_fixing_parser_tool = Tool(
            name="output_fixing_parser_tool",
            func=self.output_fixing_parser.invoke,
            coroutine=self.output_fixing_parser.ainvoke,
            description="Sửa lỗi định dạng đầu ra để đảm bảo kết quả cuối cùng là một JSON hoàn chỉnh. PHẢI sử dụng cuối cùng để hoàn thiện output.",
        )

        self.tools = [
            self.retriever_document_tool,
            self.generate_lesson_structure_tool,
            # self.output_fixing_parser_tool,
        ]

    def _init_agent(self):
        """Khởi tạo agent."""
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import (
            ChatPromptTemplate,
            HumanMessagePromptTemplate,
            MessagesPlaceholder,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=SYSTEM_PROMPT_TEMPLATE),
                MessagesPlaceholder(variable_name="history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(self.base_llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent.with_retry(),
            tools=self.tools,
            verbose=True,
            # handle_parsing_errors=True,
        )

    @override
    @trace_agent(project_name="default", tags=["lesson", "generator"])
    async def act(self, *args, **kwargs) -> list[CreateLessonSchema]:
        """
        Thực thi quy trình tạo bài giảng bằng agent.
        """
        super().act(*args, **kwargs)
        from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
        from langchain_mongodb import MongoDBChatMessageHistory

        session_id = kwargs.get("session_id")
        if not session_id:
            raise ValueError("Cần cung cấp 'session_id' để tạo bài giảng.")

        run_config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={"session_id": session_id, "agent_type": "lesson_generator"},
            tags=["lesson", "generator", f"session:{session_id}"],
        )

        agent_with_chat_history = RunnableWithMessageHistory(
            self.agent_executor,
            history_messages_key="history",
            get_session_history=lambda: MongoDBChatMessageHistory(
                settings.MONGO_URI,
                session_id,
                self.mongodb_db_name,
                self.mongodb_collection_name,
            ),
        )

        input_data = {k: v for k, v in kwargs.items() if k in self.available_args}

        try:
            response = await agent_with_chat_history.ainvoke(
                {"input": json.dumps(input_data, ensure_ascii=False)},
                config=run_config,
            )

            if isinstance(response, dict) and response.get("output"):
                # Agent sẽ trả về một chuỗi JSON, cần parse nó
                final_lesson = self.structure_parser.parse(response["output"])
                return final_lesson.list_schema
            else:
                raise ValueError("Agent không trả về kết quả hợp lệ.")

        except Exception as e:
            print(f"Lỗi trong quá trình tạo bài giảng: {e}")
            raise Exception(f"Không thể tạo bài giảng: {str(e)}")


def get_lesson_generating_agent():
    return LessonGeneratingAgent()
