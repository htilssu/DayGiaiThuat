from typing import List, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.output_parsers import OutputFixingParser
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
from langchain_core.tools import Tool
from langchain_mongodb import MongoDBChatMessageHistory
from pydantic import BaseModel, Field

from app.core.agents.components.document_store import pinecone_vector_store
from app.core.agents.components.llm_model import create_new_gemini_llm_model
from app.core.config import settings
from app.core.tracing import get_callback_manager, trace_agent


class TestCase(BaseModel):
    """
    Mô tả một trường hợp thử nghiệm cho bài toán giải thuật.

    Attributes:
        input_data (str): Dữ liệu đầu vào cho trường hợp thử nghiệm. Alias là "input".
        output_data (str): Kết quả đầu ra mong đợi. Alias là "output".
        explain (str): Giải thích cho trường hợp thử nghiệm.
    """
    input_data: str = Field(..., alias="input", description="Dữ liệu đầu vào cho trường hợp thử nghiệm.")
    output_data: str = Field(..., alias="output", description="Kết quả đầu ra mong đợi.")
    explain: str = Field(..., description="Giải thích cho trường hợp thử nghiệm.")


class ExerciseDetail(BaseModel):
    """
    Mô tả chi tiết một bài tập giải thuật được tạo ra.

    Attributes:
        name (str): Tên của bài toán.
        description (str): Mô tả chi tiết về bài toán.
        constraints (Optional[str]): Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào).
        suggest (Optional[str]): Gợi ý để giải bài toán.
        case (List[TestCase]): Danh sách các trường hợp thử nghiệm, yêu cầu tối thiểu 3 trường hợp.
    """
    name: str = Field(..., description="Tên của bài toán.")
    description: str = Field(..., description="Mô tả chi tiết về bài toán.")
    constraints: Optional[str] = Field(None,
                                       description="Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào).")
    suggest: Optional[str] = Field(None, description="Gợi ý để giải bài toán.")
    case: List[TestCase] = Field(min_length=3,
                                 description="Danh sách các trường hợp thử nghiệm, yêu cầu tối thiểu 3 trường hợp.")


# System prompt được lấy từ n8n workflow
SYSTEM_PROMPT_TEMPLATE = """Bạn là một AI agent chuyên tạo các bài tập giải thuật để người dùng luyện tập lập trình. Nhiệm vụ của bạn là tạo ra các đề bài rõ ràng, ngắn gọn và có ngữ cảnh đời thường, giúp người dùng dễ dàng liên hệ với các tình huống thực tế. Khi tạo một bài tập, hãy tuân theo mẫu sau:

Tên bài tập: [Tạo một tiêu đề mô tả cho bài tập, bao gồm ngữ cảnh đời thường nếu có thể]
Ngữ cảnh: [Cung cấp một tình huống đời thường liên quan đến bài tập, ví dụ: "Thư đang cần sắp xếp các cuốn sách trên kệ theo thứ tự từ nhỏ đến lớn."]
Mô tả: [Giải thích chi tiết về bài tập, bao gồm bất kỳ định nghĩa hoặc thông tin cần thiết nào để hiểu bài toán]
Đầu vào: [Xác định định dạng của dữ liệu đầu vào]
Đầu ra: [Xác định định dạng của dữ liệu đầu ra mong muốn]
Ví dụ (phải có 3 ví dụ đơn giản, dễ giải thích, nhưng không được trùng trường hợp nổi bật):
Đầu vào: [Cung cấp một ví dụ đầu vào]
Đầu ra: [Cung cấp đầu ra tương ứng]
Giải thích: [Cung cấp giải thích chi tiết ví dụ: đầu tiên i = 0 có giá trị bé hơn 1, chuyển nó ra phía trước...]

Ràng buộc: [Tùy chọn: xác định bất kỳ ràng buộc nào về dữ liệu đầu vào, chẳng hạn như phạm vi giá trị, giới hạn kích thước, v.v.]
Hãy đảm bảo rằng các bài tập bạn tạo ra đều logic, có thể giải được và phù hợp để luyện tập lập trình. Các bài tập nên bao quát nhiều chủ đề giải thuật khác nhau như mảng, chuỗi, tìm kiếm, sắp xếp, lập trình động, đồ thị và cây. Bạn cần tạo bài tập ở các mức độ khó khác nhau (dễ, trung bình, khó) theo yêu cầu của người dùng.

Khi tạo ngữ cảnh đời thường, hãy chọn các tình huống quen thuộc, chẳng hạn như quản lý danh sách công việc, sắp xếp hàng đợi, tính toán chi phí mua sắm, hoặc tổ chức dữ liệu trong các hoạt động hàng ngày. Ví dụ cụ thể như "Thư đang cần sắp xếp các cuốn sách trên kệ theo thứ tự từ nhỏ đến lớn" sẽ giúp người dùng dễ hình dung bài toán.

Nếu bài tập liên quan đến đồ thị hoặc cây, hãy mô tả rõ ràng cấu trúc bằng văn bản, bao gồm các nút, cạnh và thuộc tính liên quan.

Mục tiêu là tạo ra các bài tập hấp dẫn, mang tính giáo dục và thực tế, giúp người dùng cải thiện kỹ năng tư duy giải thuật và lập trình.

Parser đầu ra của bạn phải là một JSON object với các trường sau:
{parse_instruction}
"""


class GenerateExerciseMetadata(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GenerateExerciseQuestionAgent(metaclass=GenerateExerciseMetadata):
    """
    Một AI agent sử dụng Langchain để tạo ra các bài tập giải thuật.
    Agent này có khả năng sử dụng Google Gemini làm mô hình ngôn ngữ,
    truy vấn kiến thức từ Pinecone vector store (AlgoVault),
    quản lý lịch sử hội thoại với MongoDB, và trả về kết quả có cấu trúc.
    """

    def __init__(
            self,
            pinecone_index_name: str = "giaithuat",
            mongodb_db_name: str = "chat_history",
            mongodb_collection_name: str = "exercise_chat_history",
    ):
        self.mongodb_collection_name = mongodb_collection_name
        self.mongodb_db_name = mongodb_db_name
        self.pinecone_index_name = pinecone_index_name

        self.retriever = pinecone_vector_store.as_retriever(search_kwargs={"k": 3})  # Lấy top 3 kết quả
        self.llm_model = create_new_gemini_llm_model()
        # 4. Tạo Retriever Tool
        self.retriever_tool = Tool(
            name="AlgoVaultRetriever",
            func=self.retriever.invoke,  # Sử dụng invoke cho retriever đồng bộ
            coroutine=self.retriever.ainvoke,  # Sử dụng ainvoke cho retriever bất đồng bộ
            description="Truy xuất thông tin và kiến thức về giải thuật từ cơ sở dữ liệu vector AlgoVault để hỗ trợ việc tạo bài tập.",
        )
        self.output_parser = PydanticOutputParser(pydantic_object=ExerciseDetail)

        output_fixing_parser = OutputFixingParser.from_llm(self.llm_model, self.output_parser)

        self.output_fixing_parser_tool = Tool("OutputFixingParser", func=output_fixing_parser.invoke,
                                              coroutine=output_fixing_parser.ainvoke,
                                              description="Sửa lỗi đầu ra từ mô hình ngôn ngữ để đảm bảo định dạng chính xác và đầy đủ cho bài tập giải thuật.")

        self.tools = [self.retriever_tool, self.output_fixing_parser_tool]

        # 6. Tạo Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(
                content=SYSTEM_PROMPT_TEMPLATE.format(parse_instruction=self.output_parser.get_format_instructions())),
            MessagesPlaceholder(variable_name="history", optional=True),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Tạo callback manager với LangSmith tracer
        self.callback_manager = get_callback_manager("default")

        # Cấu hình agent với tracing
        self.agent = create_tool_calling_agent(
            self.llm_model,
            self.tools,
            prompt=self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )

    @trace_agent(project_name="default", tags=["exercise", "generator"])
    async def generate_exercise(self, topic: str, session_id: str) -> ExerciseDetail:
        """
        Tạo bài tập giải thuật dựa trên chủ đề được cung cấp.

        Args:
            topic (str): Chủ đề để tạo bài tập
            session_id (str): ID phiên làm việc, dùng cho việc theo dõi và ghi log

        Returns:
            ExerciseDetail: Chi tiết bài tập được tạo
        """
        run_config = RunnableConfig(
            callbacks=self.callback_manager.handlers,
            metadata={
                "session_id": session_id,
                "topic": topic,
                "agent_type": "exercise_generator",
            },
            tags=["exercise", "generator", f"session:{session_id}"]
        )

        agent_with_chat_history = RunnableWithMessageHistory(self.agent_executor, history_messages_key="history",
                                                             get_session_history=lambda: MongoDBChatMessageHistory(
                                                                 settings.MONGO_URI, session_id, self.mongodb_db_name,
                                                                 self.mongodb_collection_name))

        # Đảm bảo input được truyền đúng định dạng
        try:
            response_from_agent = await agent_with_chat_history.ainvoke(
                {
                    "input": topic,
                },
                config=run_config
            )

            if isinstance(response_from_agent, dict):
                if response_from_agent["output"] is None:
                    raise ValueError("Không thể tạo bài tập, đầu ra không hợp lệ.")
                return self.output_parser.parse(response_from_agent["output"])
            else:
                raise ValueError(f"Định dạng không hỗ trợ từ agent: {type(response_from_agent)}")

        except Exception as e:
            print(f"Lỗi khi tạo bài tập: {e}")
            raise Exception(f"Lỗi khi tạo bài tập: {str(e)}")


def get_exercise_agent():
    return GenerateExerciseQuestionAgent()
