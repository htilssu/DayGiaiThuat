import json
from typing import override

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.llm_model import create_new_creative_llm_model
from app.core.agents.components.document_store import get_vector_store
from app.core.config import settings
from app.core.tracing import trace_agent
from app.schemas.lesson_schema import CreateLessonSchema, LessonSectionSchema

SYSTEM_PROMPT_TEMPLATE = """
Bạn là một AI agent chuyên nghiệp, có nhiệm vụ tạo ra các bài giảng lập trình và giải thuật chất lượng cao.

QUAN TRỌNG: Bạn PHẢI làm theo đúng quy trình từng bước như sau và KHÔNG ĐƯỢC DỪNG CHO ĐẾN KHI HOÀN THÀNH:

1. **Nghiên cứu tài liệu:** Sử dụng `retriever_document_tool` để tìm kiếm và thu thập thông tin liên quan đến chủ đề được yêu cầu từ kho tài liệu.
2. **Tạo cấu trúc bài giảng:** Dựa trên thông tin đã thu thập, sử dụng `generate_lesson_structure_tool` để phác thảo cấu trúc bài giảng, bao gồm các phần chính và tiêu đề.
3. **Soạn nội dung chi tiết:** Với mỗi phần trong cấu trúc, sử dụng `generate_section_content_tool` để tạo ra nội dung chi tiết, bao gồm lý thuyết, ví dụ code, hoặc câu hỏi trắc nghiệm.
4. **Hoàn thiện và kiểm tra:** Cuối cùng, sử dụng `output_fixing_parser_tool` để đảm bảo toàn bộ bài giảng được định dạng chính xác theo cấu trúc JSON yêu cầu trước khi trả về kết quả.

LƯU Ý QUAN TRỌNG:
- BẠN PHẢI THỰC HIỆN TẤT CẢ CÁC BƯỚC TRÊN. KHÔNG ĐƯỢC BỎ QUA BƯỚC NÀO.
- BẠN PHẢI TRẢ VỀ MỘT JSON HOÀN CHỈNH THEO ĐÚNG SCHEMA CreateLessonSchema
- KHÔNG ĐƯỢC DỪNG CHO ĐẾN KHI CÓ KẾT QUẢ CUỐI CÙNG
- NẾU BẠN DỪNG MÀ CHƯA HOÀN THÀNH, NGƯỜI DÙNG SẼ KHÔNG NHẬN ĐƯỢC GÌ

Hãy bắt đầu ngay với việc sử dụng retriever_document_tool để tìm kiếm thông tin về chủ đề được yêu cầu.

BƯỚC ĐẦU TIÊN BẮT BUỘC: Gọi retriever_document_tool với chủ đề được cung cấp để tìm hiểu nội dung liên quan.
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

        self.vector_store = get_vector_store("document")
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})

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

        self.structure_parser = PydanticOutputParser(pydantic_object=CreateLessonSchema)
        self.content_parser = PydanticOutputParser(pydantic_object=LessonSectionSchema)

        # Chain for generating lesson structure
        self.generate_structure_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""Bạn là một chuyên gia thiết kế chương trình học. Hãy tạo cấu trúc cho một bài giảng.

                    Trong đó bài quiz phải có:
                    - "options" phải là một object có các key là A, B, C, D (không bọc bằng dấu nháy).
                    - Không được trả về "options" là string chỉ có 1 ngoại lệ là section đó không phải là quiz thì sẽ trả về null.

                    Ví dụ đúng:
                    {
                    "type": "quiz",
                    "content": "Thuật toán nào tối ưu nhất về thời gian?",
                    "options": {
                        "A": "Thuật toán A",
                        "B": "Thuật toán B",
                        "C": "Thuật toán C",
                        "D": "Thuật toán D"
                    },
                    "answer": 0
                    }
                    """
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
        self.generate_content_chain = (
            self.generate_content_prompt
            | self.base_llm.with_structured_output(LessonSectionSchema)
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
            name="generate_lesson_structure_tool",
            func=lambda x: self.generate_structure_chain.invoke({"input": x}),
            coroutine=lambda x: self.generate_structure_chain.ainvoke({"input": x}),
            description="Tạo cấu trúc bài giảng (các phần, tiêu đề) dựa trên chủ đề và thông tin tham khảo. PHẢI sử dụng sau khi đã tìm hiểu tài liệu.",
        )

        self.generate_section_content_tool = Tool(
            name="generate_section_content_tool",
            func=lambda x: self.generate_content_chain.invoke({"input": x}),
            coroutine=lambda x: self.generate_content_chain.ainvoke({"input": x}),
            description="Tạo nội dung chi tiết cho một phần cụ thể của bài giảng. Sử dụng cho từng section trong cấu trúc đã tạo.",
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
            self.generate_section_content_tool,
            self.output_fixing_parser_tool,
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
            agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True
        )

    @override
    @trace_agent(project_name="default", tags=["lesson", "generator"])
    async def act(self, *args, **kwargs) -> CreateLessonSchema:
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
                return final_lesson
            else:
                raise ValueError("Agent không trả về kết quả hợp lệ.")

        except Exception as e:
            print(f"Lỗi trong quá trình tạo bài giảng: {e}")
            raise Exception(f"Không thể tạo bài giảng: {str(e)}")


def get_lesson_generating_agent():
    return LessonGeneratingAgent()
