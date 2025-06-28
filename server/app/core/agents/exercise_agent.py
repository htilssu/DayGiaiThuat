from typing import override

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.agents.components.llm_model import create_new_creative_llm_model
from app.core.config import settings
from app.core.tracing import trace_agent
from app.schemas.exercise_schema import ExerciseDetail

SYSTEM_PROMPT_TEMPLATE = """
Bạn là một AI agent thông minh chuyên tạo ra các bài tập giải thuật để rèn luyện và cải thiện kỹ năng lập trình.

Nhiệm vụ chính của bạn:
1. Sử dụng tool retriever_algo_vault để tìm kiếm và truy xuất thông tin về các giải thuật liên quan đến chủ đề được yêu cầu.
2. Sử dụng tool retriever_exercise để kiểm tra xem bài tập với mô tả tương tự đã tồn tại trong cơ sở dữ liệu hay chưa.
3. Dựa trên thông tin thu thập được, sử dụng tool generate_exercise để tạo ra một bài tập phù hợp với chủ đề và độ khó được yêu cầu.
4. Kiểm tra và sửa lỗi đầu ra bằng tool output_fixing_parser để đảm bảo định dạng chính xác.

Nguyên tắc khi tạo bài tập:
- Bài tập phải có liên quan trực tiếp đến chủ đề (topic) được yêu cầu
- Độ khó phải phù hợp với level được chỉ định (Easy, Medium, Hard)
- Phải bao gồm đầy đủ: mô tả bài toán, input/output format, constraints, examples
- Cung cấp gợi ý hoặc hướng dẫn giải phù hợp với độ khó
- Đảm bảo bài tập có tính thực tiễn và giúp người học hiểu sâu về giải thuật

Quy trình làm việc:
1. Trước tiên, sử dụng retriever_algo_vault để tìm hiểu về chủ đề giải thuật
2. Kiểm tra với retriever_exercise xem đã có bài tập tương tự chưa
3. Tạo bài tập mới với generate_exercise
4. Sử dụng output_fixing_parser để đảm bảo format đúng

Hãy luôn đảm bảo rằng bài tập được tạo ra có chất lượng cao và mang tính giáo dục tốt.
"""

SYSTEM_PROMPT_TEMPLATE_FOR_EXERCISE_GENERATOR = """
Bạn là một chuyên gia tạo bài tập giải thuật, hãy tạo ra một bài tập hoàn chỉnh dựa trên topic và difficulty được cung cấp.

{parse_instruction}

Hãy đảm bảo bài tập:
1. Phù hợp với độ khó được yêu cầu
2. Có mô tả rõ ràng và dễ hiểu
3. Bao gồm ví dụ input/output cụ thể
4. Có constraints rõ ràng
5. Cung cấp gợi ý hữu ích

Hãy trả về kết quả theo đúng format JSON được yêu cầu.
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

        # Lazy import và setup output parser
        self._init_parsers_and_chains()

        # Lazy import và setup tools
        self._init_tools()

        # Lazy import và setup agent
        self._init_agent()

    def _init_parsers_and_chains(self):
        """Khởi tạo parsers và chains với lazy import"""
        # Lazy import - chỉ import khi cần thiết
        from langchain_core.output_parsers import PydanticOutputParser
        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import (
            ChatPromptTemplate,
            MessagesPlaceholder,
            HumanMessagePromptTemplate,
        )

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

    def _init_tools(self):
        """Khởi tạo tools với lazy import"""
        # Lazy import - chỉ import khi cần thiết
        from langchain_core.tools import Tool
        from langchain.output_parsers import OutputFixingParser

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

    def _init_agent(self):
        """Khởi tạo agent với lazy import"""
        # Lazy import - chỉ import khi cần thiết
        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import (
            ChatPromptTemplate,
            MessagesPlaceholder,
            HumanMessagePromptTemplate,
        )
        from langchain.agents import AgentExecutor, create_tool_calling_agent

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

        # Lazy import - chỉ import khi cần thiết
        from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
        from langchain_mongodb import MongoDBChatMessageHistory

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
