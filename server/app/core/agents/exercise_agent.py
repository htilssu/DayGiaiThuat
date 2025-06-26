from typing import override

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.output_parsers import OutputFixingParser
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
)
from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
from langchain_core.tools import Tool
from langchain_mongodb import MongoDBChatMessageHistory

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.agents.components.llm_model import create_new_creative_llm_model
from app.core.config import settings
from app.core.tracing import trace_agent
from app.schemas.exercise_schema import ExerciseDetail

SYSTEM_PROMPT_TEMPLATE_FOR_EXERCISE_GENERATOR = """
Bạn là chuyên gia tạo các bài tập giải thuật để người dùng luyện tập lập trình.
Nhiệm vụ của bạn là tạo ra các đề bài rõ ràng, ngắn gọn và có ngữ cảnh đời thường,
giúp người dùng dễ dàng liên hệ với các tình huống thực tế.
Bài tập được tạo ra phải không trùng
với bài tập đã tồn tại trong cơ sở dữ liệu.
Bài tập giống như leetcode Khi tạo một bài tập, hãy tuân theo mẫu sau:

Tên bài tập: [Tạo một tiêu đề mô tả cho bài tập, bao gồm ngữ cảnh đời thường nếu có thể]
Mô tả: [Giải thích chi tiết về bài tập, bao gồm bất kỳ định nghĩa hoặc thông tin cần thiết nào để hiểu bài toán]
Đầu vào: [dữ liệu đầu vào]
Đầu ra: [dữ liệu đầu ra mong muốn]
Ví dụ (phải có 3 ví dụ đơn giản, dễ giải thích, nhưng không được trùng trường hợp nổi bật,
đầu vào và ra phải là string và theo format để người dùng có thể dùng code để đọc đầu vào và xử lý):
Đầu vào: [Cung cấp một ví dụ đầu vào]
Đầu ra: [Cung cấp đầu ra tương ứng]
ví dụ:
dòng đầu là t định nghĩa số tập dữ liệu
t dòng tiếp theo chứa m,n,k
đầu vào: "3
2 3 4
5 6 7
8 9 10
"
đầu ra là kết quả của từng tập dữ liệu được tách ra bởi dấu xuống dòng
đầu ra: "
2
5
6
"
Giải thích: [Cung cấp giải thích chi tiết ví dụ: đầu tiên i = 0 có giá trị bé hơn 1, chuyển nó ra phía trước...]

Ràng buộc: [Tùy chọn: xác định bất kỳ ràng buộc nào về dữ liệu đầu vào,
chẳng hạn như phạm vi giá trị, giới hạn kích thước, v.v.]
Hãy đảm bảo rằng các bài tập bạn tạo ra đều logic, có thể giải được và phù hợp để luyện tập lập trình.
Các bài tập nên bao quát nhiều chủ đề giải thuật khác nhau như mảng,
chuỗi, tìm kiếm, sắp xếp, lập trình động, đồ thị và cây
Bạn cần tạo bài tập ở các mức độ khó khác nhau (dễ, trung bình, khó) theo yêu cầu của người dùng.

Khi tạo ngữ cảnh đời thường, hãy chọn các tình huống quen thuộc,
chẳng hạn như quản lý danh sech công việc, sắp xếp hàng đợi, tính toán chi phí mua sắm,
hoặc tổ chức dữ liệu trong các hoạt động hàng ngày.
Ví dụ cụ thể như "Thư đang cần sắp xếp các cuốn sách trên kệ theo thứ tự từ nhỏ đến lớn"
sẽ giúp người dùng dễ hình dung bài toán.

Nếu bài tập liên quan đến đồ thị hoặc cây,
hãy mô tả rõ ràng cấu trúc bằng văn bản, bao gồm các nút, cạnh và thuộc tính liên quan.

Mục tiêu là tạo ra các bài tập hấp dẫn, mang tính giáo dục và thực tế,
giúp người dùng cải thiện kỹ năng tư duy giải thuật và lập trình.

Parser đầu ra của bạn phải là một JSON object với các trường sau:

{parse_instruction}
"""


# System prompt được lấy từ n8n workflow
SYSTEM_PROMPT_TEMPLATE = """
Bạn là 1 chuyên gia hàng đầu trong việc tạo các bài tập giải thuật để người dùng luyện tập lập trình.
Nhiệm vụ của bạn là tạo ra các đề bài rõ ràng, ngắn gọn và có ngữ cảnh đời thường,
giúp người dùng dễ dàng liên hệ với các tình huống thực tế. Bài tập được tạo ra phải không trùng
với bài tập đã tồn tại trong cơ sở dữ liệu.

Sử dụng dữ liệu trong cơ sở dữ liệu để tạo ra các bài tập giải thuật mới - Nếu không có dữ liệu,
hãy tạo ra bài tập dựa trên các thông tin mà bạn đã được train.
Sau khi tạo bài tập, hãy kiểm tra xem bài tập đã tồn tại trong cơ sở dữ liệu
hay chưa
(lấy description của bài tập để kiểm tra).
Nếu tồn tại rồi thì tạo lại bài tập mới.
Nếu 1 bài tập đã tồn tại trong cơ sở dữ liệu, hãy tạo ra bài tập mới dựa trên các thông tin đã có.
"""


class GenerateExerciseQuestionAgent(BaseAgent):
    """
    Một AI agent sử dụng Langchain để tạo ra các bài tập giải thuật.
    Agent này có khả năng sử dụng Google Gemini làm mô hình ngôn ngữ,
    truy vấn kiến thức từ Pinecone vector store (AlgoVault),
    quản lý lịch sử hội thoại với MongoDB, và trả về kết quả có cấu trúc.
    """

    def __init__(
        self,
        mongodb_db_name: str = "chat_history",
        mongodb_collection_name: str = "exercise_chat_history",
    ):
        super().__init__()
        self.available_args = ["topic", "session_id", "difficulty"]
        self.mongodb_collection_name = mongodb_collection_name
        self.mongodb_db_name = mongodb_db_name

        self.retriever = get_vector_store("giaithuat").as_retriever(
            search_kwargs={"k": 3}
        )  # Lấy top 3 kết quả

        self.exercise_retriever = get_vector_store("exercise").as_retriever(
            search_kwargs={"k": 1}
        )  # Lấy 1 kết quả
        self.output_parser = PydanticOutputParser(pydantic_object=ExerciseDetail)

        self.generate_exercise_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=SYSTEM_PROMPT_TEMPLATE_FOR_EXERCISE_GENERATOR.format(
                        parse_instruction=self.output_parser.get_format_instructions()
                    )
                ),
                MessagesPlaceholder(variable_name="history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

        self.generate_exercise = (
            self.generate_exercise_prompt
            | create_new_creative_llm_model().with_structured_output(ExerciseDetail)
        )

        self.retriever_tool = Tool(
            name="retriever_algo_vault",
            func=self.retriever.invoke,  # Sử dụng invoke cho retriever đồng bộ
            coroutine=self.retriever.ainvoke,  # Sử dụng ainvoke cho retriever bất đồng bộ
            description="""Truy xuất thông tin và kiến thức về giải thuật từ cơ sở dữ liệu
            vector AlgoVault để hỗ trợ việc tạo bài tập.""",
        )

        self.retriever_exercise_tool = Tool(
            name="retriever_exercise",
            func=self.exercise_retriever.invoke,  # Sử dụng invoke cho retriever đồng bộ
            coroutine=self.exercise_retriever.ainvoke,  # Sử dụng ainvoke cho retriever bất đồng bộ
            description="""Truy xuất thông tin về các bài tập đã được lưu trong cơ sở dữ liệu.
            Để kiểm tra xem bài tập đã tồn tại trong cơ sở dữ liệu hay chưa.
            sử dụng description của bài tập để kiểm tra""",
        )

        self.generate_exercise_tool = Tool(
            name="generate_exercise",
            func=lambda x: self.generate_exercise.invoke(
                {"input": x} if isinstance(x, str) else x
            ),
            coroutine=lambda x: self.generate_exercise.ainvoke(
                {"input": x} if isinstance(x, str) else x
            ),
            description="""Tạo bài tập giải thuật mới dựa trên input là topic và difficulty được cung cấp.,
            đầu vào là biến input""",
        )

        self.output_fixing_parser = OutputFixingParser.from_llm(
            self.base_llm, self.output_parser
        )

        self.output_fixing_parser_tool = Tool(
            "OutputFixingParser",
            func=self.output_fixing_parser.invoke,
            coroutine=self.output_fixing_parser.ainvoke,
            description="""Sửa lỗi đầu ra từ mô hình ngôn ngữ để đảm bảo định dạng chính
            xác và đầy đủ cho bài tập giải thuật.""",
        )

        self.tools = [
            self.retriever_tool,
            self.retriever_exercise_tool,
            self.generate_exercise_tool,
            self.output_fixing_parser_tool,
        ]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=SYSTEM_PROMPT_TEMPLATE),
                MessagesPlaceholder(variable_name="history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.agent = create_tool_calling_agent(
            self.base_llm,
            self.tools,
            prompt=self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=True, handle_parsing_errors=True
        )

    @override
    @trace_agent(project_name="default", tags=["exercise", "generator"])
    async def act(self, *args, **kwargs):
        """
        Tạo bài tập giải thuật và lưu vào cơ sở dữ liệu.

        Args:
            topic (str): Chủ đề của bài tập
            session_id (str): ID phiên làm việc
            difficulty (str): Độ khó của bài tập
            topic_id (int): ID của chủ đề trong database
            db (AsyncSession, optional): Phiên làm việc với database

        Returns:
            ExerciseDetail: Chi tiết bài tập được tạo ra
            Exercise: Đối tượng Exercise đã được lưu vào database
        """
        super().act(*args, **kwargs)

        topic = kwargs.get("topic", "")
        session_id = kwargs.get("session_id", "")
        difficulty = kwargs.get("difficulty", "")

        if not topic or not session_id or not difficulty:
            raise ValueError(
                "Cần cung cấp 'topic', 'session_id' và 'difficulty' để tạo bài tập."
            )

        run_config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={
                "session_id": session_id,
                "topic": topic,
                "difficulty": difficulty,
                "agent_type": "exercise_generator",
            },
            tags=["exercise", "generator", f"session:{session_id}"],
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
            response_from_agent = await agent_with_chat_history.ainvoke(
                {
                    "input": "topic: " + topic + ", difficulty: " + difficulty,
                },
                config=run_config,
            )

            if isinstance(response_from_agent, dict):
                if response_from_agent["output"] is None:
                    raise ValueError("Không thể tạo bài tập, đầu ra không hợp lệ.")

                # Phân tích kết quả từ agent
                exercise_detail = self.output_fixing_parser.parse(
                    response_from_agent["output"]
                )

                return exercise_detail
            else:
                raise ValueError(
                    f"Định dạng không hỗ trợ từ agent: {type(response_from_agent)}"
                )

        except Exception as e:
            print(f"Lỗi khi tạo bài tập: {e}")
            raise Exception(f"Lỗi khi tạo bài tập: {str(e)}")


def get_exercise_agent():
    return GenerateExerciseQuestionAgent()
