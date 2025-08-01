from app.core.agents.base_agent import BaseAgent
from app.models.course_model import Course
from app.utils.model_utils import model_to_dict
from pydantic import BaseModel, Field, ValidationError
from app.core.tracing import trace_agent
from typing import override, Dict, Any
import logging
import asyncio
from google.api_core.exceptions import (
    InternalServerError,
    DeadlineExceeded,
    ServiceUnavailable,
)

from app.database.database import get_independent_db_session
from sqlalchemy import select

logger = logging.getLogger(__name__)

AGENT_PROMPT = """
Bạn là chuyên gia đánh giá năng lực học sinh. Nhiệm vụ của bạn là tạo ra một bài kiểm tra đầu vào có tính phân hóa cao,
giúp đánh giá chính xác trình độ hiện tại của học sinh đối với toàn bộ nội dung của khóa học.

Yêu cầu:
- Đề bài phải bao phủ đầy đủ các chủ đề chính trong khóa học, từ cơ bản đến nâng cao.
- Mỗi câu hỏi cần đánh giá một kỹ năng hoặc kiến thức cụ thể.
- Phân loại độ khó câu hỏi theo 3 mức: Dễ (kiến thức nền tảng), Trung bình (vận dụng), Khó (vận dụng cao hoặc nâng cao).
- Bố cục đề nên xen kẽ các mức độ khó để tránh học sinh bị nản hoặc chủ quan.
- Đề phải có khả năng phân loại học sinh thành các nhóm trình độ: yếu, trung bình, khá, giỏi.
- Mỗi câu hỏi cần có nội dung rõ ràng, không gây hiểu nhầm, và có thể chấm điểm khách quan.

Mục tiêu cuối cùng là giúp xác định chính xác học sinh đang ở đâu trong hành trình học tập
và từ đó đề xuất lộ trình học phù hợp.
Bài kiểm tra sẽ có các định dạng sau:
{test_format}
"""


class Question(BaseModel):
    content: str = Field(description="Nội dung câu hỏi")
    difficulty: str = Field(description="Độ khó của câu hỏi")
    type: str = Field(
        description="Loại câu hỏi",
        enum=[
            "single_choice",
            "multiple_choice",
            "essay",
        ],
    )
    answer: str = Field(description="Câu trả lời đúng")
    options: list[str] = Field(description="Các câu trả lời sai")


class InputTestAgentOutput(BaseModel):
    questions: list[Question] = Field(description="Danh sách câu hỏi")
    course_id: int = Field(description="ID của khóa học")


class InputTestAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.available_args = ["course_id"]
        self._output_parser = None
        self._output_fix_parser = None
        self._prompt = None
        self._tool_calling_agent = None
        self._agent_executor = None

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds

        # Khởi tạo tool với lazy import
        self._init_tools()

    def _init_tools(self):
        """Khởi tạo tools với lazy import"""
        # Lazy import - chỉ import khi cần thiết
        from langchain_core.tools import Tool

        async def get_course_by_id(course_id: int):
            async with get_independent_db_session() as db:
                result = await db.execute(select(Course).filter(Course.id == course_id))
                course = result.scalars().first()
                return model_to_dict(course)

        self.tools = [
            Tool.from_function(
                name="get_course_by_id",
                func=get_course_by_id,
                coroutine=get_course_by_id,
                description="Get the course by id",
            ),
        ]

    @property
    def output_parser(self):
        if self._output_parser is None:
            # Lazy import - chỉ import khi cần thiết
            from langchain_core.output_parsers import PydanticOutputParser

            self._output_parser = PydanticOutputParser(
                pydantic_object=InputTestAgentOutput
            )
        return self._output_parser

    @property
    def output_fix_parser(self):
        if self._output_fix_parser is None:
            # Lazy import - chỉ import khi cần thiết
            from langchain.output_parsers import OutputFixingParser

            self._output_fix_parser = OutputFixingParser.from_llm(
                llm=self.base_llm,
                parser=self.output_parser,
            )
        return self._output_fix_parser

    @property
    def prompt(self):
        if self._prompt is None:
            # Lazy import - chỉ import khi cần thiết
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.messages import SystemMessage
            from langchain_core.prompts import HumanMessagePromptTemplate
            from langchain_core.prompts.chat import MessagesPlaceholder

            self._prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(
                        content=AGENT_PROMPT.format(
                            test_format=self.output_parser.get_format_instructions()
                        )
                    ),
                    HumanMessagePromptTemplate.from_template("{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
        return self._prompt

    @property
    def tool_calling_agent(self):
        if self._tool_calling_agent is None:
            # Lazy import - chỉ import khi cần thiết
            from langchain.agents import create_tool_calling_agent

            self._tool_calling_agent = create_tool_calling_agent(
                llm=self.base_llm,
                tools=self.tools,
                prompt=self.prompt,
            )
        return self._tool_calling_agent

    @property
    def agent_executor(self):
        if self._agent_executor is None:
            # Lazy import - chỉ import khi cần thiết
            from langchain.agents import AgentExecutor

            self._agent_executor = AgentExecutor.from_agent_and_tools(
                agent=self.tool_calling_agent,
                tools=self.tools,
                verbose=True,
            )
        return self._agent_executor

    async def _execute_with_retry(
        self, input_data: Dict[str, Any], config: Any
    ) -> Dict[str, Any]:
        """
        Thực thi agent với retry logic cho Google AI API errors

        Args:
            input_data: Input cho agent
            config: Runnable config

        Returns:
            Dict: Kết quả từ agent

        Raises:
            Exception: Sau khi hết số lần retry
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f"Đang thực thi agent, lần thử {attempt + 1}/{self.max_retries}"
                )
                result = await self.agent_executor.ainvoke(input_data, config=config)
                logger.info("Thực thi agent thành công")
                return result

            except (InternalServerError, DeadlineExceeded, ServiceUnavailable) as e:
                last_exception = e
                logger.warning(f"Google AI API error (lần {attempt + 1}): {e}")

                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2**attempt)  # Exponential backoff
                    logger.info(f"Đợi {delay} giây trước khi thử lại...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Đã thử {self.max_retries} lần nhưng vẫn thất bại")

            except Exception as e:
                # Lỗi khác không cần retry
                logger.error(f"Lỗi không thể retry: {e}")
                raise e

        # Nếu đã hết số lần retry
        if last_exception:
            raise Exception(
                f"Google AI API không khả dụng sau {self.max_retries} lần thử. Lỗi: {last_exception}"
            )
        else:
            raise Exception(f"Không thể thực thi agent sau {self.max_retries} lần thử")

    async def _parse_output_with_fix(
        self, output: Dict[str, Any], course_id: int
    ) -> InputTestAgentOutput:
        """
        Parse output từ agent với khả năng fix lỗi format

        Args:
            output: Output từ agent
            course_id: ID của khóa học

        Returns:
            InputTestAgentOutput: Kết quả đã parse
        """
        if not output or "output" not in output:
            raise ValueError("Output không hợp lệ từ agent")

        output_text = output["output"]

        try:
            # Thử parse bằng parser chính
            result = self.output_parser.parse(output_text)
            result.course_id = course_id
            return result

        except ValidationError as e:
            logger.warning(f"Lỗi parse, sử dụng fixing parser: {e}")
            try:
                # Sử dụng fixing parser
                result = self.output_fix_parser.parse(output_text)
                result.course_id = course_id
                return result
            except Exception as fix_error:
                logger.error(f"Fixing parser cũng thất bại: {fix_error}")
                raise ValueError(f"Không thể parse output: {fix_error}")

    @override
    @trace_agent(project_name="default", tags=["input_test", "agent"])
    async def act(self, *args, **kwargs):
        super().act(*args, **kwargs)

        course_id = kwargs.get("course_id")
        if not course_id:
            raise ValueError("Thiếu course_id")

        # Lazy import - chỉ import khi cần thiết
        from langchain_core.runnables import RunnableConfig

        config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={"course_id": course_id, "agent_type": "input_test"},
            tags=["input_test", "agent", f"course:{course_id}"],
        )

        input_data = {"input": f"Tạo bài kiểm tra đầu vào cho khóa học ID: {course_id}"}

        try:
            # Thực thi với retry
            output = await self._execute_with_retry(input_data, config)

            # Parse output
            result = await self._parse_output_with_fix(output, course_id)

            logger.info(f"Tạo thành công {len(result.questions)} câu hỏi")
            return result

        except Exception as e:
            logger.error(f"Lỗi trong InputTestAgent.act: {e}")
            raise Exception(f"Lỗi tạo bài kiểm tra: {str(e)}")


def get_input_test_agent():
    return InputTestAgent()
