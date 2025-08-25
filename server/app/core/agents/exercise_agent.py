from typing import override

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.agents.components.llm_model import create_new_llm_model
from typing import Any, cast
import re
from app.core.config import settings
from app.core.tracing import trace_agent
from app.schemas.exercise_schema import ExerciseDetail

# Expected test case format for frontend compatibility:
# testCases: [
#   {
#     "input": "input data as string",
#     "expectedOutput": "expected output as string"
#   }
# ]
# This matches the format used in web/src/data/mockExercises.ts

SYSTEM_PROMPT_TEMPLATE = """
Bạn là một chuyên gia, chuyên tạo ra các bài tập giải thuật để rèn luyện và cải thiện kỹ năng lập trình.

# Nhiệm vụ chính của bạn:
1. Sử dụng tool retriever_algo_vault để tìm kiếm và truy xuất thông tin về các giải thuật liên quan đến chủ đề được yêu cầu.
2. Sử dụng tool retriever_exercise để kiểm tra xem bài tập với mô tả tương tự đã tồn tại trong cơ sở dữ liệu hay chưa.
3. Dựa trên thông tin thu thập được, sử dụng tool generate_exercise để tạo ra một bài tập phù hợp với chủ đề, bài học và độ khó được yêu cầu.
4. Kiểm tra và sửa lỗi đầu ra bằng tool output_fixing_parser để đảm bảo định dạng chính xác.

# Quy trình làm việc:
1. Trước tiên, sử dụng retriever_algo_vault để tìm hiểu về chủ đề giải thuật
2. Kiểm tra với retriever_exercise xem đã có bài tập tương tự chưa
3. Nếu chưa có bài tập tương tự tạo bài tập mới với generate_exercise

# Tham số đầu vào:
- tool generate_exercise: sẽ mô tả ngữ cảnh về topic, lesson và difficulty để tạo bài tập, khái niệm về lesson sẽ được sử dụng để tạo bài tập. cần tránh những ngữ cảnh không liên quan ví dụ: `Hãy tạo một bài tập theo thông tin sau:
        - Chủ đề: Giới thiệu về Lập trình
        - Bài học: Các khái niệm cơ bản về biến, kiểu dữ liệu và toán tử (tóm tắt ngắn gọn về lesson đầu vào, học sinh đã học được gì từ lesson này và tạo bài tập cho phù hợp)
        - Độ khó: trung bình
        - Chỉ sử dụng các khái niệm: biến, kiểu dữ liệu cơ bản, toán tử số học, ép kiểu, input/output đơn giản
        - Không được sử dụng các ngữ cảnh: bài toán tài chính, lãi suất, ứng dụng thực tế phức tạp, vòng lặp, hàm`


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

# Quan trọng về testCases:
- testCases phải là một mảng chứa ít nhất 3 test case
- Mỗi test case phải có format: {{"input": "dữ liệu đầu vào", "expectedOutput": "kết quả mong đợi"}}
- Input và expectedOutput phải là string
- Input nên bao gồm các tham số cần thiết (ví dụ: "[1,2,3], 2" cho hàm nhận mảng và số)
- ExpectedOutput phải chính xác và dễ hiểu

# Quy ước CHẶT CHẼ cho input:
# - Luôn gói TOÀN BỘ input trong MỘT mảng, dạng chuỗi JSON HỢP LỆ: ví dụ
#   + "[1,2,3]" thay vì "1,2,3"
#   + "[[1,2,3,4],5]" thay vì "[1,2,3,4], 5"
# - Nhớ dấu phẩy giữa các phần tử trong mảng (JSON bắt buộc phải có dấu phẩy)
# - Nếu hàm nhận nhiều tham số (a, b, c), hãy đặt TẤT CẢ vào một mảng duy nhất
#   và mỗi phần tử PHẢI cách nhau bằng dấu phẩy: ví dụ "[a, b, c]"
# - Nếu hàm chỉ nhận một tham số, vẫn để trong mảng: ví dụ "[42]"

# Suy nghĩ kỹ:
- Khi người dùng học bài này thì họ đã có những kiến thức gì trước đó, nếu mới nhập môn thì cần tránh những ngữ cảnh quá phức tạp

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
            search_kwargs={"k": 2}
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
            top_p=0.9, temperature=0.7
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
            agent=self.agent, tools=self.tools, verbose=True, handle_parsing_errors=True
        )

    @staticmethod
    def _normalize_input_array_string(raw: str) -> str:
        """
        Ensure input is a single JSON-like array string with commas between items.
        Examples:
          "1, 2, 3"     -> "[1, 2, 3]"
          "[1 2 3]"     -> "[1, 2, 3]"
          "[1,2,3], 5"  -> "[[1, 2, 3], 5]"
          "[ [1 2],3 ]" -> "[[1, 2], 3]"
        """
        s = (raw or "").strip()
        if not s:
            return "[]"

        # Wrap if not already an array
        if not (s.startswith("[") and s.endswith("]")):
            s = f"[{s}]"

        # If looks like multi-arg e.g. "[...], 5", wrap whole into an outer array
        if "]," in s and not (s.startswith("[[") and s.endswith("]]")):
            s = f"[{s}]"

        # Insert commas where numbers are separated only by whitespace inside arrays
        # Handle integers, negatives, and decimals
        def add_commas(segment: str) -> str:
            # add comma between number tokens separated by spaces
            segment = re.sub(r"(?<=\d)\s+(?=[-]?\d)", ", ", segment)
            # also add comma after closing bracket before number e.g. "] 5" -> "], 5"
            segment = re.sub(r"(?<=\])\s+(?=[-]?\d)", ", ", segment)
            # and between number then opening bracket e.g. "5 [1,2]" -> "5, [1,2]"
            segment = re.sub(r"(?<=\d)\s+(?=\[)", ", ", segment)
            return segment

        # Apply within the whole string (safe enough for our simple normalization)
        s = add_commas(s)
        return s

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
        lesson_ctx = kwargs.get("lesson", None)

        # Require either topic or lesson context, plus session and difficulty
        if (not topic and not lesson_ctx) or not session_id or not difficulty:
            raise ValueError(
                "Cần cung cấp 'lesson' hoặc 'topic', kèm 'session_id' và 'difficulty' để tạo bài tập."
            )

        from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
        from langchain_mongodb import MongoDBChatMessageHistory

        run_config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={
                "session_id": session_id,
                "topic": topic,
                "lesson_title": (lesson_ctx or {}).get("name") if isinstance(lesson_ctx, dict) else None,
                "difficulty": difficulty,
                "agent_type": "exercise_generator",
            },
            tags=["exercise", "generator", f"session:{session_id}"],
        )

        agent_with_chat_history = RunnableWithMessageHistory(
            cast(Any, self.agent_executor),
            history_messages_key="history",
            get_session_history=lambda: MongoDBChatMessageHistory(
                settings.MONGO_URI,
                session_id,
                self.mongodb_db_name,
                self.mongodb_collection_name,
            ),
        )

        try:
            # Prefer lesson-based query if provided; fallback to topic
            if lesson_ctx and isinstance(lesson_ctx, dict):
                lesson_title = lesson_ctx.get("name") or lesson_ctx.get("title") or ""
                lesson_desc = lesson_ctx.get("description") or ""
                query = f"lesson: {lesson_title} - {lesson_desc}, difficulty: {difficulty}"
            else:
                query = f"topic: {topic}, difficulty: {difficulty}"

            response_from_agent = await agent_with_chat_history.ainvoke(
                {
                    "input": query,
                    "lesson": lesson_ctx,
                },
                config=run_config,
            )

            if isinstance(response_from_agent, dict):
                if response_from_agent["output"] is None:
                    raise ValueError("Không thể tạo bài tập, đầu ra không hợp lệ.")

                exercise_detail = self.output_fixing_parser.parse(
                    response_from_agent["output"]
                )

                # Validate and ensure testCases format is correct
                if hasattr(exercise_detail, 'testCases') and exercise_detail.testCases:
                    for test_case in exercise_detail.testCases:
                        if not hasattr(test_case, 'input') or not hasattr(test_case, 'expectedOutput'):
                            raise ValueError("Test case format không đúng. Cần có 'input' và 'expectedOutput' fields.")
                        if not isinstance(test_case.input, str) or not isinstance(test_case.expectedOutput, str):
                            raise ValueError("Test case input và expectedOutput phải là string.")

                        # Normalize input to always be a single JSON-like array string with commas
                        test_case.input = self._normalize_input_array_string(test_case.input)

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
