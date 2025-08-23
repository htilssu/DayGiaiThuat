from typing import override

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.agents.components.llm_model import create_new_llm_model
from app.core.config import settings
from app.core.tracing import trace_agent
from app.schemas.exercise_schema import ExerciseDetail

SYSTEM_PROMPT_TEMPLATE = """
Bạn là một chuyên gia, chuyên tạo ra các bài tập giải thuật để rèn luyện và cải thiện kỹ năng lập trình.

# Nhiệm vụ chính của bạn:
1. Sử dụng tool retriever_algo_vault để tìm kiếm và truy xuất thông tin về các giải thuật liên quan đến chủ đề được yêu cầu.
2. # Suy nghĩ kỹ:
    - Khi người dùng học bài này thì họ đã có những kiến thức gì trước đó, nếu mới nhập môn thì cần tránh những ngữ cảnh quá phức tạp
3. Dựa trên thông tin thu thập được, sử dụng tool generate_exercise để tạo ra một bài tập phù hợp với chủ đề, bài học và độ khó được yêu cầu đặc biệt là phải vừa sức với học sinh.
4. Sử dụng tool retriever_exercise để kiểm tra xem bài tập với mô tả tương tự đã tồn tại trong cơ sở dữ liệu hay chưa nếu đã tồn tại thì quay lại bước 3.

# Quy trình làm việc:
1. Trước tiên, sử dụng retriever_algo_vault để tìm hiểu về chủ đề giải thuật
2. Kiểm tra với retriever_exercise xem đã có bài tập tương tự chưa
3. Nếu chưa có bài tập tương tự tạo bài tập mới với generate_exercise

# Tham số đầu vào:
- tool generate_exercise: sẽ mô tả ngữ cảnh về topic, lesson và difficulty để tạo bài tập, khái niệm về lesson sẽ được sử dụng để tạo bài tập. cần tránh những ngữ cảnh không liên quan
    *ví dụ*: ```Hãy tạo một bài tập theo thông tin sau:
        - Chủ đề: Giới thiệu về Lập trình
        - Bài học: Các khái niệm cơ bản về biến, kiểu dữ liệu và toán tử (tóm tắt ngắn gọn về lesson đầu vào, học sinh đã học được gì từ lesson này và tạo bài tập cho phù hợp)
        - Độ khó: trung bình
        - Chỉ sử dụng các khái niệm: biến, kiểu dữ liệu cơ bản, toán tử số học, ép kiểu, input/output đơn giản
        - Không được sử dụng các ngữ cảnh: bài toán tài chính, lãi suất, ứng dụng thực tế phức tạp, vòng lặp, hàm
        - Loại bài tập: executable=false (bài tập lý thuyết về khái niệm) hoặc executable=true (bài tập viết code)```

# Hướng dẫn về loại bài tập:
- executable=true: Tạo bài tập lập trình với input/output cụ thể, test cases để học sinh viết code
- executable=false: Tạo bài tập lý thuyết, giải thích khái niệm, phân tích thuật toán không cần viết code


Hãy luôn đảm bảo rằng bài tập được tạo ra có chất lượng cao và mang tính giáo dục tốt.
"""

SYSTEM_PROMPT_TEMPLATE_FOR_EXERCISE_GENERATOR = """
Bạn là một chuyên gia tạo bài tập giải thuật, hãy tạo ra một bài tập hoàn chỉnh dựa trên topic, lesson và difficulty được cung cấp.

Hãy đảm bảo bài tập:
1. Phù hợp với độ khó được yêu cầu
2. Có mô tả rõ ràng và dễ hiểu
3. Bao gồm ví dụ input/output cụ thể
4. Có constraints rõ ràng
5. Cung cấp gợi ý hữu ích
6. Bám sát ngữ cảnh của lesson
7. Xác định loại bài tập phù hợp (executable hoặc non-executable):
   - executable=true: Bài tập lập trình cần viết code để giải quyết (có input/output cụ thể, test cases)
   - executable=false: Bài tập lý thuyết, giải thích khái niệm, phân tích thuật toán (không cần viết code)

# Suy nghĩ kỹ:
- Khi người dùng học bài này thì họ đã có những kiến thức gì trước đó, nếu mới nhập môn thì cần tránh những ngữ cảnh quá phức tạp
- Xác định xem bài học tập trung vào lý thuyết hay thực hành để chọn loại bài tập phù hợp
- Với các bài học về khái niệm cơ bản, có thể tạo bài tập lý thuyết (executable=false)
- Với các bài học về thuật toán cụ thể, nên tạo bài tập lập trình (executable=true)

Hãy trả về kết quả theo đúng format JSON được yêu cầu.

{parse_instruction}
"""


class GenerateExerciseQuestionAgent(BaseAgent):
    def __init__(
        self,
        mongodb_db_name: str = "chat_history",
        mongodb_collection_name: str = "exercise_chat_history",
    ):
        super().__init__()
        self.available_args = ["topic", "session_id", "difficulty", "lesson"]
        self.mongodb_collection_name = mongodb_collection_name
        self.mongodb_db_name = mongodb_db_name

        self.retriever = get_vector_store("document").as_retriever(
            search_kwargs={"k": 3}
        )

        self.exercise_retriever = get_vector_store("exercise").as_retriever(
            search_kwargs={"k": 3}
        )

        self._init_parsers_and_chains()

        self._init_tools()

        self._init_agent()

    def _init_parsers_and_chains(self):
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

        self.generate_exercise = self.generate_exercise_prompt | create_new_llm_model(
            top_p=0.9, temperature=0.6
        ).with_structured_output(ExerciseDetail)

    def _init_tools(self):
        from langchain_core.tools import Tool
        from langchain.output_parsers import OutputFixingParser

        self.retriever_tool = Tool(
            name="retriever_algo_vault",
            func=self.retriever.invoke,
            coroutine=self.retriever.ainvoke,
            description="""Truy xuất thông tin và kiến thức về giải thuật từ cơ sở dữ liệu
            vector AlgoVault để hỗ trợ việc tạo bài tập.""",
        )

        self.retriever_exercise_tool = Tool(
            name="retriever_exercise",
            func=self.exercise_retriever.invoke,
            coroutine=self.exercise_retriever.ainvoke,
            description="""Truy xuất thông tin về các bài tập đã được lưu trong cơ sở dữ liệu.
            Để kiểm tra xem bài tập đã tồn tại trong cơ sở dữ liệu hay chưa.
            sử dụng description của bài tập để kiểm tra""",
        )

        self.generate_exercise_tool = Tool(
            name="generate_exercise",
            func=self.generate_exercise.invoke,
            coroutine=self.generate_exercise.ainvoke,
            description="""Tạo bài tập giải thuật mới dựa trên input là topic, lesson và difficulty được cung cấp.,
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

        self._tools = [
            self.retriever_tool,
            self.retriever_exercise_tool,
            self.generate_exercise_tool,
        ]

    @property
    def tools(self):
        if self._tools is None:
            self._init_tools()
        return self._tools

    def _init_agent(self):
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
            agent=self.agent.with_retry(stop_after_attempt=5),
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
        )

    @override
    @trace_agent(project_name="default", tags=["exercise", "generator"])
    async def act(self, *args, **kwargs):
        """
        Tạo bài tập giải thuật và lưu vào cơ sở dữ liệu.

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
                    "lesson": kwargs.get("lesson", None),
                },
                config=run_config,
            )

            if isinstance(response_from_agent, dict):
                if response_from_agent["output"] is None:
                    raise ValueError("Không thể tạo bài tập, đầu ra không hợp lệ.")

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
