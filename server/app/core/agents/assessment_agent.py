import asyncio
import logging
from typing import Any, Dict, List, override

from fastapi import Depends
from pydantic import BaseModel, Field
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
Bạn là một chuyên gia đánh giá và tư vấn giáo dục trong lĩnh vực lập trình và giải thuật.

Nhiệm vụ của bạn:
1. Phân tích người dùng
2. Đánh giá trình độ hiện tại và xác định điểm mạnh/yếu
3. Tạo lộ trình học tập cá nhân hóa phù hợp với trình độ
4. Đưa ra khuyến nghị cụ thể để cải thiện kỹ năng

Tools có sẵn:
- get_test_session_data: Lấy dữ liệu phiên thi chi tiết
- get_course_topics: Lấy danh sách chủ đề của khóa học
- analyze_performance: Phân tích hiệu suất chi tiết
- generate_learning_path: Tạo lộ trình học tập

Nguyên tắc đánh giá:
- Dựa trên tỷ lệ đúng/sai tổng thể
- Phân tích theo từng chủ đề cụ thể
- Xem xét độ khó của các câu hỏi
- Đánh giá thời gian làm bài
- Tính toán mức độ hiểu biết của từng concept

Hãy luôn đưa ra phân tích khách quan và lời khuyên hữu ích để giúp người học phát triển.
"""


class AssessmentAgent(BaseAgent):
    """
    Agent đánh giá trình độ người dùng dựa trên kết quả bài kiểm tra đầu vào
    và tạo lộ trình học tập cá nhân hóa
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

        # Initialize tools
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
            Tool(
                name="analyze_performance",
                func=lambda x: asyncio.run(self._analyze_performance(x)),
                coroutine=self._analyze_performance,
                description="""Phân tích hiệu suất chi tiết theo từng chủ đề
                Input: test_session_data (dict)""",
            ),
            Tool(
                name="generate_learning_path",
                func=lambda x: asyncio.run(self._generate_learning_path(x)),
                coroutine=self._generate_learning_path,
                description="""Tạo lộ trình học tập dựa trên kết quả phân tích
                Input: analysis_data (dict)""",
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
                        Hãy đánh giá kết quả bài kiểm tra đầu vào của người dùng và tạo lộ trình học tập.
                        Thông tin cần xử lý:
                        - Test Session ID: {test_session_id}
                        - User ID: {user_id}
                        Hãy sử dụng các tools có sẵn để:
                        1. Lấy dữ liệu phiên thi
                        2. Phân tích hiệu suất
                        3. Tạo lộ trình học tập
                        Trả về kết quả đánh giá đầy đủ theo format JSON.
                        Format output:
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

    async def _analyze_performance(
        self, test_session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phân tích hiệu suất chi tiết"""
        try:
            answers = test_session_data.get("user_answers", [])
            if not answers:
                return {"error": "Không có dữ liệu câu trả lời"}

            total_questions = len(answers)
            correct_answers = sum(
                1 for answer in answers if answer.get("is_correct", False)
            )
            score_percentage = (
                (correct_answers / total_questions) * 100 if total_questions > 0 else 0
            )

            # Phân tích theo chủ đề (nếu có)
            topic_analysis = {}
            for answer in answers:
                topic = answer.get("topic", "Unknown")
                if topic not in topic_analysis:
                    topic_analysis[topic] = {"correct": 0, "total": 0}

                topic_analysis[topic]["total"] += 1
                if answer.get("is_correct", False):
                    topic_analysis[topic]["correct"] += 1

            # Xác định điểm mạnh và yếu
            strengths = []
            weaknesses = []

            for topic, stats in topic_analysis.items():
                accuracy = (
                    stats["correct"] / stats["total"] if stats["total"] > 0 else 0
                )
                if accuracy >= 0.8:
                    strengths.append(topic)
                elif accuracy < 0.5:
                    weaknesses.append(topic)

            return {
                "total_questions": total_questions,
                "correct_answers": correct_answers,
                "score_percentage": score_percentage,
                "topic_analysis": topic_analysis,
                "strengths": strengths,
                "weaknesses": weaknesses,
            }
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {"error": str(e)}

    async def _generate_learning_path(
        self, analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Tạo lộ trình học tập"""
        try:
            score_percentage = analysis_data.get("score_percentage", 0)
            weaknesses = analysis_data.get("weaknesses", [])

            # Xác định độ khó phù hợp
            if score_percentage >= 80:
                difficulty_level = "Advanced"
            elif score_percentage >= 60:
                difficulty_level = "Intermediate"
            else:
                difficulty_level = "Beginner"

            # Tạo lộ trình dựa trên điểm yếu
            learning_path = []
            for i, weakness in enumerate(weaknesses):
                learning_path.append(
                    {
                        "topic_name": weakness,
                        "priority": len(weaknesses) - i,  # Ưu tiên cao cho điểm yếu đầu
                        "estimated_time": 4,  # 4 giờ mỗi chủ đề
                        "difficulty": difficulty_level,
                        "description": f"Cải thiện kỹ năng trong {weakness}",
                    }
                )

            return learning_path
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
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
                    # Parse the output using the output parser
                    agent_result = output_parser.parse(result["output"])

                    # Convert AgentAssessmentSchema to AssessmentResult
                    assessment_result = AssessmentResult(
                        type="test",
                        strengths=agent_result.strengths,
                        weaknesses=agent_result.weaknesses,
                        recommendations=agent_result.recommendations,
                        skill_levels=agent_result.skill_levels,
                        learning_path=agent_result.learning_path,
                        overall_score=agent_result.overall_score,
                        proficiency_level=agent_result.proficiency_level,
                        analysis_summary=agent_result.analysis_summary,
                    )
                    return assessment_result
                except Exception as parse_error:
                    logger.warning(f"Primary parser failed: {parse_error}")
                    # Try with fixing parser
                    fixing_parser = self._get_output_fix_parser()
                    agent_result = fixing_parser.parse(result["output"])

                    # Convert AgentAssessmentSchema to AssessmentResult
                    assessment_result = AssessmentResult(
                        type="test",
                        strengths=agent_result.strengths,
                        weaknesses=agent_result.weaknesses,
                        recommendations=agent_result.recommendations,
                        skill_levels=agent_result.skill_levels,
                        learning_path=agent_result.learning_path,
                        overall_score=agent_result.overall_score,
                        proficiency_level=agent_result.proficiency_level,
                        analysis_summary=agent_result.analysis_summary,
                    )
                    return assessment_result
            else:
                raise ValueError(f"Unexpected result format: {type(result)}")

        except Exception as e:
            logger.error(f"Error in assessment agent: {e}")
            # Return a default assessment result
            return AssessmentResult(
                type="test",
                strengths=[],
                weaknesses=[],
                recommendations=["Hoàn thành bài kiểm tra để nhận đánh giá chi tiết"],
            )


def get_assessment_agent(
    test_service: TestService = Depends(get_test_service),
    course_service: CourseService = Depends(get_course_service),
    session: AsyncSession = Depends(get_async_db),
):
    """Dependency injection cho AssessmentAgent"""
    return AssessmentAgent(test_service, course_service, session)
