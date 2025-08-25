import asyncio
import logging
from typing import Any, Dict, List, override

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.agents.base_agent import BaseAgent
from app.core.tracing import trace_agent
from app.database.database import get_async_db
from app.schemas.assessment_schema import AssessmentResult, ASSESSMENT_TYPE
from app.services.course_service import CourseService, get_course_service
from app.services.test_service import TestService, get_test_service
from app.utils.model_utils import model_to_dict

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
Bạn là một chuyên gia phân tích và đánh giá điểm yếu trong lĩnh vực lập trình và giải thuật.

Nhiệm vụ của bạn:
1. Phân tích kết quả bài kiểm tra để xác định điểm yếu cụ thể của người dùng trong từng skill
2. Đánh giá mức độ nghiêm trọng của các điểm yếu
3. Phân tích chi tiết nguyên nhân dẫn đến điểm yếu
4. Đưa ra gợi ý cụ thể để cải thiện từng điểm yếu

Tools có sẵn:
- get_test_session_data: Lấy dữ liệu phiên thi chi tiết
- get_course_topics: Lấy danh sách chủ đề của khóa học

Nguyên tắc phân tích điểm yếu:
- Tập trung vào những câu hỏi sai hoặc làm chậm
- Phân tích theo từng skill/chủ đề cụ thể
- Xác định pattern lỗi thường gặp
- Đánh giá mức độ nghiêm trọng: Low/Medium/High
- Tính toán mức độ hiểu biết hiện tại của skill
- Tự động tạo gợi ý cải thiện phù hợp

Luôn đưa ra phân tích chi tiết, khách quan về điểm yếu và gợi ý cải thiện thực tế.
"""


class AssessmentAgent(BaseAgent):
    """
    Agent phân tích điểm yếu của người dùng dựa trên kết quả bài kiểm tra
    và đưa ra gợi ý cải thiện cụ thể cho từng skill
    """

    def __init__(
        self,
        test_service: TestService,
        course_service: CourseService,
        session: AsyncSession,
    ):
        super().__init__()
        self.test_service = test_service
        self.course_service = course_service
        self.session = session
        self.available_args = ["test_session_id", "user_id"]

        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2

        # Initialize output parser
        self._output_parser = None
        self._output_fix_parser = None
        self._prompt = None
        self._agent_executor = None

        self._init_tools()

    def _init_tools(self):
        """Khởi tạo các tools cho agent với lazy import"""
        from langchain_core.tools import Tool

        self.tools = [
            Tool(
                name="get_test_session_data",
                func=lambda x: asyncio.run(self._get_test_session_data(x)),
                coroutine=self._get_test_session_data,
                description="""Lấy dữ liệu chi tiết của phiên thi bao gồm:
                - Kết quả từng câu hỏi
                - Thời gian làm bài
                - Điểm số và tỷ lệ đúng
                Input: test_session_id (str)""",
            ),
            Tool(
                name="get_course_topics",
                func=lambda x: asyncio.run(self._get_course_topics(x)),
                coroutine=self._get_course_topics,
                description="""Lấy danh sách tất cả chủ đề trong khóa học
                Input: course_id (int)""",
            ),
        ]

    def _get_output_parser(self):
        if self._output_parser is None:
            from langchain_core.output_parsers import PydanticOutputParser

            from app.schemas.assessment_schema import AgentAssessmentSchema

            self._output_parser = PydanticOutputParser(
                pydantic_object=AgentAssessmentSchema
            )
        return self._output_parser

    def _get_output_fix_parser(self):
        """Lazy initialization của output fixing parser"""
        if self._output_fix_parser is None:
            from langchain.output_parsers import OutputFixingParser

            self._output_fix_parser = OutputFixingParser.from_llm(
                self.base_llm, self._get_output_parser()
            )
        return self._output_fix_parser

    def _get_prompt(self):
        if self._prompt is None:
            from langchain_core.messages import SystemMessage
            from langchain_core.prompts import (
                ChatPromptTemplate,
                MessagesPlaceholder,
                HumanMessagePromptTemplate,
            )

            self._prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessagePromptTemplate.from_template(
                        """
                        Hãy phân tích điểm yếu của người dùng dựa trên kết quả bài kiểm tra.
                        Thông tin cần xử lý:
                        - Test Session ID: {test_session_id}
                        - User ID: {user_id}
                        Hãy sử dụng tool để lấy dữ liệu phiên thi, sau đó tự phân tích:
                        1. Lấy dữ liệu phiên thi
                        2. Tự phân tích điểm yếu từ câu trả lời sai
                        3. Xác định skill có vấn đề nhất
                        4. Đánh giá mức độ nghiêm trọng
                        5. Tự tạo gợi ý cải thiện phù hợp
                        Phân tích chi tiết:
                        - Xem xét từng câu sai để tìm pattern
                        - Xác định skill/topic có tỷ lệ sai cao nhất
                        - Đánh giá mức độ hiện tại dựa trên kết quả
                        - Tạo gợi ý cải thiện cụ thể cho skill đó
                        Trả về kết quả phân tích điểm yếu theo format JSON:
                        {format_instructions}
                        """
                    ),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
        return self._prompt

    def _get_agent_executor(self):
        """Lazy initialization của agent executor"""
        if self._agent_executor is None:
            from langchain.agents import AgentExecutor, create_tool_calling_agent

            prompt = self._get_prompt()

            agent = create_tool_calling_agent(
                self.base_llm,
                self.tools,
                prompt=prompt,
            )

            self._agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=10,
            )
        return self._agent_executor

    async def _get_test_session_data(self, test_session_id: str) -> Dict[str, Any]:
        """Lấy dữ liệu chi tiết phiên thi"""
        try:
            test_session = await self.test_service.get_test_session(test_session_id)
            if not test_session:
                raise ValueError(f"Không tìm thấy phiên thi với ID: {test_session_id}")

            test_session_data = model_to_dict(test_session)

            return {
                "test_session": test_session_data,
                "total_questions": len(test_session_data.get("answers", [])),
                "user_answers": test_session_data.get("answers", []),
                "score": test_session_data.get("score", 0),
                "status": test_session_data.get("status", ""),
                "start_time": str(test_session_data.get("start_time", "")),
                "end_time": str(test_session_data.get("end_time", "")),
            }
        except Exception as e:
            logger.error(f"Error getting test session data: {e}")
            return {"error": str(e)}

    async def _get_course_topics(self, course_id: int) -> List[Dict[str, Any]]:
        """Lấy danh sách chủ đề khóa học"""
        try:
            course = await self.course_service.get_course(course_id, None)
            if course and hasattr(course, "topics"):
                return [model_to_dict(topic) for topic in course.topics]
            return []
        except Exception as e:
            logger.error(f"Error getting course topics: {e}")
            return []

    @override
    @trace_agent(project_name="default", tags=["assessment", "evaluation"])
    async def act(self, *args, **kwargs) -> AssessmentResult:
        assessment_type: ASSESSMENT_TYPE = kwargs.get(
            "assessment_type", ASSESSMENT_TYPE
        )

        test_session_id = None
        user_id = None

        if assessment_type == "test":
            test_session_id = kwargs.get("test_session_id")
            user_id = kwargs.get("user_id")

        if not test_session_id or not user_id:
            raise ValueError("Cần cung cấp test_session_id và user_id")

        try:
            from langchain_core.runnables import RunnableConfig

            config = RunnableConfig(
                callbacks=self._callback_manager.handlers,
                metadata={
                    "test_session_id": test_session_id,
                    "user_id": user_id,
                    "agent_type": "assessment",
                },
                tags=["assessment", "evaluation", f"user:{user_id}"],
            )

            agent_executor = self._get_agent_executor()
            output_parser = self._get_output_parser()

            result = await agent_executor.ainvoke(
                {
                    "test_session_id": test_session_id,
                    "user_id": user_id,
                    "format_instructions": output_parser.get_format_instructions(),
                },
                config=config,
            )

            if isinstance(result, dict) and "output" in result:
                try:
                    agent_result = output_parser.parse(result["output"])

                    assessment_result = AssessmentResult(
                        type="test",
                        skill_name=agent_result.skill_name,
                        weaknesses=agent_result.weaknesses,
                        weakness_analysis=agent_result.weakness_analysis,
                        improvement_suggestions=agent_result.improvement_suggestions,
                        current_level=agent_result.current_level,
                        weakness_severity=agent_result.weakness_severity,
                    )
                    return assessment_result
                except Exception as parse_error:
                    logger.warning(f"Primary parser failed: {parse_error}")
                    # Try with fixing parser
                    fixing_parser = self._get_output_fix_parser()
                    agent_result = fixing_parser.parse(result["output"])

                    assessment_result = AssessmentResult(
                        type="test",
                        skill_name=agent_result.skill_name,
                        weaknesses=agent_result.weaknesses,
                        weakness_analysis=agent_result.weakness_analysis,
                        improvement_suggestions=agent_result.improvement_suggestions,
                        current_level=agent_result.current_level,
                        weakness_severity=agent_result.weakness_severity,
                    )
                    return assessment_result
            else:
                raise ValueError(f"Unexpected result format: {type(result)}")

        except Exception as e:
            logger.error(f"Error in assessment agent: {e}")
            # Return a default assessment result
            return AssessmentResult(
                type="test",
                skill_name="General Programming",
                weaknesses=["Chưa có dữ liệu đánh giá"],
                weakness_analysis="Cần hoàn thành bài kiểm tra để phân tích chi tiết",
                improvement_suggestions=[
                    "Hoàn thành bài kiểm tra để nhận đánh giá chi tiết"
                ],
                current_level="Unknown",
                weakness_severity="Low",
            )


def get_assessment_agent(
    test_service: TestService = Depends(get_test_service),
    course_service: CourseService = Depends(get_course_service),
    session: AsyncSession = Depends(get_async_db),
):
    """Dependency injection cho AssessmentAgent"""
    return AssessmentAgent(test_service, course_service, session)
