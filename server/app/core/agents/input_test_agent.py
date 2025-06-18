from app.core.agents.base_agent import BaseAgent
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
"""


class InputTestAgent(BaseAgent):
    def __init__(self, course_service: CourseService):
        super().__init__()
        self.course_service = course_service
        self.available_args = ["course_id"]

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

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=AGENT_PROMPT),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.tool_calling_agent = create_tool_calling_agent(
            llm=self.base_llm,
            tools=self.tools,
            prompt=self.prompt,
        )

    async def act(self, *args, **kwargs):
        super().act(*args, **kwargs)
        course_id = kwargs.get("course_id")
        if not course_id:
            raise ValueError("course_id is required")
        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.tool_calling_agent,
            tools=self.tools,
            verbose=True,
        )
        return await agent_executor.ainvoke({"input": f"course_id: {course_id}"})


def get_input_test_agent(course_service: CourseService = Depends(get_course_service)):
    return InputTestAgent(course_service)
