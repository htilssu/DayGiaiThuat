from app.core.agents.base_agent import BaseAgent
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import Tool
from fastapi import Depends
from app.services.course_service import CourseService, get_course_service
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts.chat import MessagesPlaceholder
from langchain.agents import AgentExecutor
from app.models.course_model import Course
from app.utils.model_utils import model_to_dict
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
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
    def __init__(self, course_service: CourseService):
        super().__init__()
        self.course_service = course_service
        self.available_args = ["course_id"]
        self._output_parser = None
        self._output_fix_parser = None
        self._prompt = None
        self._tool_calling_agent = None
        self._agent_executor = None

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds

        # Khởi tạo tool ngay vì nó không tốn nhiều tài nguyên
        async def get_course_by_id(course_id: int):
            course: Course = await self.course_service.get_course_by_id(course_id)
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
            self._output_parser = PydanticOutputParser(
                pydantic_object=InputTestAgentOutput
            )
        return self._output_parser

    @property
    def output_fix_parser(self):
        if self._output_fix_parser is None:
            self._output_fix_parser = OutputFixingParser.from_llm(
                llm=self.base_llm,
                parser=self.output_parser,
            )
        return self._output_fix_parser

    @property
    def prompt(self):
        if self._prompt is None:
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
            self._tool_calling_agent = create_tool_calling_agent(
                llm=self.base_llm,
                tools=self.tools,
                prompt=self.prompt,
            )
        return self._tool_calling_agent

    @property
    def agent_executor(self):
        if self._agent_executor is None:
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

    async def _parse_output(
        self, output: Dict[str, Any], course_id: int
    ) -> InputTestAgentOutput:
        """
        Phân tích và chuyển đổi output từ agent thành đối tượng InputTestAgentOutput

        Args:
            output: Kết quả từ agent executor
            course_id: ID của khóa học

        Returns:
            InputTestAgentOutput: Đối tượng đã được phân tích

        Raises:
            ValueError: Nếu không thể phân tích output
        """
        try:
            # Thử phân tích trực tiếp
            if isinstance(output, dict) and "output" in output:
                raw_output = output["output"]
            else:
                raw_output = output

            # Sử dụng output fixing parser để sửa lỗi nếu cần
            parsed_output = self.output_fix_parser.parse(raw_output)

            # Đảm bảo course_id được thiết lập đúng
            if parsed_output.course_id != course_id:
                parsed_output.course_id = course_id

            return parsed_output
        except ValidationError as e:
            logger.error(f"Lỗi validation khi phân tích output: {e}")
            # Thử phương pháp khác nếu phân tích thất bại
            try:
                # Tạo một đối tượng mới với course_id đã biết
                return InputTestAgentOutput(
                    questions=output.get("questions", []), course_id=course_id
                )
            except Exception as e2:
                logger.error(f"Không thể khôi phục từ lỗi phân tích: {e2}")
                raise ValueError(f"Không thể phân tích output từ agent: {e}, {e2}")

    @override
    @trace_agent(project_name="default", tags=["input_test", "agent"])
    async def act(self, *args, **kwargs):
        super().act(*args, **kwargs)
        course_id = kwargs.get("course_id")
        if not course_id:
            raise ValueError("course_id is required")

        run_config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={
                "course_id": course_id,
                "agent_type": "input_test_generator",
            },
            tags=["input_test", "generator", f"course:{course_id}"],
        )

        try:
            # Thực thi agent với retry logic
            result = await self._execute_with_retry(
                {"input": f"course_id: {course_id}"}, run_config
            )

            # Phân tích kết quả bằng output parser
            parsed_result = await self._parse_output(result, course_id)

            return parsed_result

        except Exception as e:
            logger.error(f"Lỗi khi thực thi agent: {e}")

            # Tạo thông báo lỗi thân thiện hơn
            if "Google AI" in str(e) or "Internal" in str(e):
                error_message = (
                    "Dịch vụ AI tạm thời không khả dụng. Vui lòng thử lại sau vài phút."
                )
            elif "timeout" in str(e).lower() or "deadline" in str(e).lower():
                error_message = (
                    "Quá trình tạo test mất quá nhiều thời gian. Vui lòng thử lại."
                )
            else:
                error_message = f"Lỗi không xác định: {e}"

            raise ValueError(error_message)


def get_input_test_agent(course_service: CourseService = Depends(get_course_service)):
    return InputTestAgent(course_service)
