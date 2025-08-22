from typing import List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import SystemMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from tenacity import retry, wait_exponential, stop_after_attempt

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.config import settings
from app.core.tracing import trace_agent
from app.models import Topic
from app.schemas import AgentCreateLessonSchema
from app.schemas.topic_schema import TopicBase

SYSTEM_PROMPT_TEMPLATE = """
Bạn là một chuyên gia thiết kế chương trình học, có nhiệm vụ tạo ra các bài giảng lập trình và giải thuật chất lượng cao.

QUAN TRỌNG: Bạn PHẢI làm theo đúng quy trình từng bước như sau và KHÔNG ĐƯỢC DỪNG CHO ĐẾN KHI HOÀN THÀNH:

1. **Nghiên cứu tài liệu:** Sử dụng `retriever_document_tool` để tìm kiếm và thu thập thông tin liên quan đến chủ đề được yêu cầu từ kho tài liệu (có thể gọi nhiều lần để truy vấn dữ liệu đầy đủ nhất).
2. **Tạo bài giảng:** Dựa trên thông tin đã thu thập, phác thảo bài giảng và  tạo bài giảng chi tiết,gồm nhiều lesson (một topic có nhiều lesson) có chắt lọc thông tin từ retriever_document_tool để đưa vào cho 1 đoạn văn bản.

LƯU Ý QUAN TRỌNG:
- BẠN PHẢI THỰC HIỆN TẤT CẢ CÁC BƯỚC TRÊN. KHÔNG ĐƯỢC BỎ QUA BƯỚC NÀO.
- Cho dù không đủ thông tin yêu cầu vẫn phải đi theo luồng của quy trình. KHÔNG ĐƯỢC YÊU CẦU BỔ SUNG THÊM THÔNG TIN.
- KHÔNG ĐƯỢC DỪNG CHO ĐẾN KHI CÓ KẾT QUẢ CUỐI CÙNG

# TẠO BÀI GIẢNG:
    Hãy tạo cấu trúc cho nhiều bài giảng (lesson) dựa vào đầu vào.
    
    Hướng dẫn về từng loại section:
    - "teaching": Phần giảng dạy, truyền đạt kiến thức, có thể chứa giải thích, ví dụ, hướng dẫn
    - "quiz": Phần câu hỏi trắc nghiệm để kiểm tra hiểu biết của học viên
    - "text": Phần văn bản thuần túy
    - "code": Phần code mẫu hoặc ví dụ lập trình
    - "image": Phần hình ảnh minh họa
    - "exercise": Phần bài tập thực hành để học viên áp dụng kiến thức đã học
    
    Đối với section loại "quiz":
    - "options" phải là một object có các key là A, B, C, D (không bọc bằng dấu nháy).
    - "answer" phải là một trong các giá trị: "A", "B", "C", "D"
    - Phải có "explanation" để giải thích đáp án
    
    Đối với các section khác (teaching, text, code, image):
    - "options" phải là null
    - "answer" phải là null
    - "explanation" phải là null
    
    # QUAN TRỌNG VỀ NỘI DUNG:
    - Mỗi bài giảng phải có phần ví dụ dễ hiểu, giúp học viên nắm vững kiến thức.
    - Nội dung có thể sử dụng Markdown formatting để tăng tính đọc hiểu:
      * Sử dụng **bold** cho từ khóa quan trọng
      * Sử dụng *italic* cho nhấn mạnh
      * Sử dụng `code` cho thuật ngữ kỹ thuật
      * Sử dụng ### cho tiêu đề phụ
      * Sử dụng - hoặc 1. cho danh sách
      * Sử dụng > cho blockquote khi trích dẫn
      * Sử dụng ```language cho code blocks trong section "code"
    # Quan trọng:
    - Phải dựa vào layout của bài giảng từ đầu vào, không được tự ý thay đổi cấu trúc.
    - Bài giảng hoặc giới thiệu luôn nằm ở đầu tiên, sau đó là các phần khác.
    - Trường exercise là phần bài tập vận dụng (nó là phần có cấu trúc của section exercise), section exercise sẽ trình bày mô tả, ngữ cảnh bài tập, hướng dẫn thực hiện và các yêu cầu cụ thể.
    - Mỗi lession bắt buộc phải có exercise để vận dụng
    - Dưới mỗi bài giảng, cần có phần tóm tắt ngắn gọn các điểm chính đã học,phải thêm ví dụ và phần triển khai để người dùng hiểu rõ hơn.
    - Phải có phần bài tập ví dụ (bài tập này phải được giải thích kỹ),sau bài tập ví dụ đó có 1 bài tập vận dụng để học viên thực hành, Phần vận dụng hoặc bài tập sẽ nằm sau phần lý thuyết liên quan.
    - Type của section phải là một trong các giá trị sau: "text", "code", "quiz", "manipulate","teaching", "image", "exercise".

# OUTPUT FORMAT
    {{
      "list_schema": [
        {{
          "title": "Tiêu đề bài học",
          "description": "Mô tả ngắn gọn về bài học",
          "order": 1,
          "topic_id": 8,
          "sections": [
            {{
              "type": "teaching",
              "order": 1
              "content": "Nội dung bài giảng dạng markdown hoặc text",
              "options": null,
              "answer": null,
              "explanation": null
            }},
            {{
              "type": "quiz",
              "order": 2
              "content": "Câu hỏi trắc nghiệm",
              "options": {{
                "A": "Đáp án A",
                "B": "Đáp án B",
                "C": "Đáp án C",
                "D": "Đáp án D"
              }},
              "answer": "C",
              "explanation": "Giải thích tại sao đáp án đúng"
            }},
            {{
              "type": "exercise",
              "order": 3
              "content": "Bài tập mô tả yêu cầu, có thể gồm input/output mẫu",
              "options": null,
              "answer": null,
              "explanation": null
            }},
            {{
              "type": "code",
              "order": 4
              "content": "```python\n# code minh họa\nprint('hello graph')\n```",
              "options": null,
              "answer": null,
              "explanation": null
            }}
          ],
          "exercises": []
        }}
      ]
    }}
    - Chỉ trả về JSON hợp lệ

"""


class LessonGeneratingAgent(BaseAgent):
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
        from langchain_core.output_parsers import PydanticOutputParser

        from typing import List
        from pydantic import BaseModel

        class ListCreateLessonSchema(BaseModel):
            list_schema: List[AgentCreateLessonSchema]

        self.structure_parser = PydanticOutputParser(
            pydantic_object=ListCreateLessonSchema
        )


    def _init_tools(self):
        from langchain.output_parsers import OutputFixingParser
        from langchain_core.tools import Tool

        self.retriever_document_tool = Tool(
            name="retriever_document_tool",
            func=self.retriever.invoke,
            coroutine=self.retriever.ainvoke,
            description="Truy xuất tài liệu và kiến thức từ kho vector để hỗ trợ việc tạo bài giảng. BẮT BUỘC phải sử dụng tool này đầu tiên để tìm hiểu về chủ đề.",
        )

        self.output_fixing_parser = OutputFixingParser.from_llm(
            self.base_llm, self.structure_parser
        )

        self.tools = [
            self.retriever_document_tool,
        ]

    def _init_agent(self):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=SYSTEM_PROMPT_TEMPLATE
                ),
                MessagesPlaceholder(variable_name="history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(self.base_llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent.with_retry(stop_after_attempt=5),
            tools=self.tools,
            verbose=True,
        )

    @trace_agent(project_name="default", tags=["lesson", "generator"])
    @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
    async def act(self, topic: Topic, session_id: str) -> List[AgentCreateLessonSchema]:
        from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
        from langchain_mongodb import MongoDBChatMessageHistory

        if not session_id:
            raise ValueError("Session ID không được để trống.")

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

        try:
            agent_input = TopicBase.model_validate(topic, from_attributes=True).model_dump_json()
            response = await agent_with_chat_history.ainvoke(
                {"input": agent_input},
                config=run_config,
            )

            try:
                final_lesson = self.structure_parser.parse(response["output"])
                return final_lesson.list_schema
            except Exception as e:
                return (
                    await self.output_fixing_parser.ainvoke(response["output"])
                ).list_schema
        except Exception as e:
            print(f"Lỗi trong quá trình tạo Lesson: {e}")
            raise Exception(f"Không thể tạo bài giảng: {str(e)}")


async def get_lesson_generating_agent():
    return LessonGeneratingAgent()
