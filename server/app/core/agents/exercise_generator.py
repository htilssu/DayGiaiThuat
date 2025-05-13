from typing import List, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_pinecone import PineconeVectorStore
from pydantic import BaseModel as LangchainBaseModel, Field as LangchainField

from app.core.agents.components.embedding_model import gemini_embedding_model
from app.core.agents.components.llm_model import llm_model_name, gemini_llm_model
from app.core.config import settings
from app.core.service.pinecone_component import pc_index


class TestCase(LangchainBaseModel):
    """
    Mô tả một trường hợp thử nghiệm cho bài toán giải thuật.

    Attributes:
        input_data (str): Dữ liệu đầu vào cho trường hợp thử nghiệm. Alias là "input".
        output_data (str): Kết quả đầu ra mong đợi. Alias là "output".
        explain (str): Giải thích cho trường hợp thử nghiệm.
    """
    input_data: str = LangchainField(..., alias="input", description="Dữ liệu đầu vào cho trường hợp thử nghiệm.")
    output_data: str = LangchainField(..., alias="output", description="Kết quả đầu ra mong đợi.")
    explain: str = LangchainField(..., description="Giải thích cho trường hợp thử nghiệm.")


class ExerciseDetail(LangchainBaseModel):
    """
    Mô tả chi tiết một bài tập giải thuật được tạo ra.

    Attributes:
        name (str): Tên của bài toán.
        description (str): Mô tả chi tiết về bài toán.
        constraints (Optional[str]): Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào).
        suggest (Optional[str]): Gợi ý để giải bài toán.
        case (List[TestCase]): Danh sách các trường hợp thử nghiệm, yêu cầu tối thiểu 3 trường hợp.
    """
    name: str = LangchainField(..., description="Tên của bài toán.")
    description: str = LangchainField(..., description="Mô tả chi tiết về bài toán.")
    constraints: Optional[str] = LangchainField(None,
                                                description="Các ràng buộc của bài toán (ví dụ: giới hạn đầu vào).")
    suggest: Optional[str] = LangchainField(None, description="Gợi ý để giải bài toán.")
    case: List[TestCase] = LangchainField(..., min_items=3,
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

Hãy đảm bảo câu trả lời của bạn tuân thủ định dạng JSON được mô tả bởi schema sau:
{format_instructions}
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
        """
        Khởi tạo GenerateExerciseQuestionAgent.

        Args:
            pinecone_index_name (str): Tên của Pinecone index. Mặc định là "giaithuat".
            mongodb_db_name (str): Tên database MongoDB để lưu lịch sử chat. Mặc định là "chat_history".
            mongodb_collection_name (str): Tên collection MongoDB để lưu lịch sử chat. Mặc định là "exercise_sessions".

        Raises:
            ValueError: Nếu thiếu các API key hoặc thông tin cấu hình cần thiết.
        """
        self.mongodb_collection_name = mongodb_collection_name
        self.mongodb_db_name = mongodb_db_name
        self.pinecone_index_name = pinecone_index_name
        self.google_api_key = settings.GOOGLE_API_KEY
        self.mongodb_uri = settings.MONGO_URI

        if not self.google_api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass as argument.")
        if not self.mongodb_uri:
            raise ValueError("MongoDB URI is required. Set MONGODB_URI environment variable or pass as argument.")

        # 3. Khởi tạo Pinecone Vector Store và Retriever
        self.vector_store = PineconeVectorStore(index=pc_index, embedding=gemini_embedding_model)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})  # Lấy top 3 kết quả

        # 4. Tạo Retriever Tool
        self.retriever_tool = Tool(
            name="AlgoVaultRetriever",
            func=self.retriever.invoke,  # Sử dụng invoke cho retriever đồng bộ
            coroutine=self.retriever.ainvoke,  # Sử dụng ainvoke cho retriever bất đồng bộ
            description="Truy xuất thông tin và kiến thức về giải thuật từ cơ sở dữ liệu vector AlgoVault để hỗ trợ việc tạo bài tập.",
        )
        self.tools = [self.retriever_tool]

        self.output_parser = PydanticOutputParser(pydantic_object=ExerciseDetail)

        # 6. Tạo Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=SYSTEM_PROMPT_TEMPLATE.format(
                format_instructions=self.output_parser.get_format_instructions())),
            MessagesPlaceholder(variable_name="history", optional=True),
            HumanMessage(content="{input}"),
        ])

        # 7. Tạo Agent
        # Lưu ý: create_tool_calling_agent thường dùng cho các model hỗ trợ "tool calling" rõ ràng.
        # Gemini hỗ trợ điều này, nhưng cú pháp prompt và cách agent hoạt động có thể cần điều chỉnh.
        # Nếu gặp vấn đề, có thể xem xét create_structured_chat_agent hoặc các loại agent khác.
        agent = create_tool_calling_agent(gemini_llm_model, self.tools, self.prompt)

        # 8. Tạo Agent Executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,  # Đặt thành False trong production
            handle_parsing_errors=True  # Xử lý lỗi parsing, có thể trả về thông báo lỗi cho người dùng hoặc thử lại
        )

    def _get_session_history(self, session_id: str) -> MongoDBChatMessageHistory:
        """
        Lấy hoặc tạo lịch sử hội thoại cho một session_id cụ thể từ MongoDB.

        Args:
            session_id (str): ID của session hội thoại.

        Returns:
            MongoDBChatMessageHistory: Đối tượng lịch sử hội thoại.
        """
        return MongoDBChatMessageHistory(
            connection_string=settings.MONGO_URI,
            session_id=session_id,
            database_name=self.mongodb_db_name,
            collection_name=self.mongodb_collection_name,
        )

    async def generate_exercise(self, topic: str, session_id: str) -> ExerciseDetail:
        """
        Tạo một bài tập giải thuật dựa trên yêu cầu của người dùng.

        Args:
            topic (str): Chủ đề của bài tập.
            session_id (str): ID của session hội thoại để duy trì ngữ cảnh.

        Returns:
            ExerciseDetail: Đối tượng Pydantic chứa chi tiết bài tập đã được tạo.

        Raises:
            Exception: Nếu có lỗi trong quá trình tạo bài tập hoặc parsing kết quả.
        """

        config : RunnableConfig = {"configurable": {"session_id": session_id}}

        history_runnable = RunnableWithMessageHistory(self.agent_executor, self._get_session_history,
                                                      input_messages_key="input", history_messages_key="history")

        response_from_agent = await history_runnable.ainvoke({
            "input": topic,
        }, config=config)

        if isinstance(response_from_agent, dict):
            response_content = response_from_agent.get("output")
            if response_content is None:

                print(f"Warning: 'output' key not found in agent response. Full response: {response_from_agent}")
                try:
                    parsed_exercise = ExerciseDetail.model_validate(response_from_agent)
                    return parsed_exercise
                except Exception:  # Not our target structure
                    response_content = str(response_from_agent)  # Fallback to string representation
        elif isinstance(response_from_agent, str):
            response_content = response_from_agent
        else:
            raise ValueError(f"Unexpected response type from agent: {type(response_from_agent)}")

        if not response_content:
            raise Exception("Agent did not produce any output content to parse.")

        try:
            # Phân tích cú pháp output của agent
            parsed_exercise = self.output_parser.parse(response_content)
        except Exception as e:
            print(f"Error parsing LLM output: {e}")
            print(f"Raw output was: {response_content}")
            # Fallback: cố gắng parse bằng JsonOutputParser nếu PydanticOutputParser thất bại
            try:
                print("Attempting fallback JSON parsing...")
                json_parser = JsonOutputParser(pydantic_object=ExerciseDetail)
                parsed_exercise = json_parser.parse(response_content)
            except Exception as e2:
                raise Exception(
                    f"Failed to parse agent output into ExerciseDetail structure. Original error: {e}. Fallback error: {e2}. Raw output: {response_content}") from e2

        return parsed_exercise


def get_exercise_agent():
    return GenerateExerciseQuestionAgent()
