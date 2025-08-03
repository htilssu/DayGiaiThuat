"""
Course Composition Agent - Tạo danh sách topics cho khóa học
"""

import json
import logging
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.course_schema import (
    CourseCompositionRequestSchema,
    CourseCompositionResponseSchema,
    TopicGenerationResult,
)

logger = logging.getLogger(__name__)


class CourseAgentResponse(BaseModel):
    """Response model cho Course Composition Agent"""

    topics: List[TopicGenerationResult] = Field(
        ..., description="Danh sách topics với skills"
    )
    duration: str = Field(
        ..., description="Thời gian ước lượng hoàn thành khóa học (VD: '4-6 tuần', '20 giờ')"
    )


def validate_topics(topics: List[TopicGenerationResult]) -> bool:
    """
    Validate danh sách topics được tạo
    """
    if not topics:
        return False

    # Kiểm tra order sequence
    orders = [topic.order for topic in topics]
    if sorted(orders) != list(range(1, len(topics) + 1)):
        logger.warning("Topic orders are not sequential")

    # Kiểm tra skills
    for topic in topics:
        if not topic.skills or len(topic.skills) < 2:
            logger.warning(f"Topic '{topic.name}' has insufficient skills")
            return False

    return True


class CourseCompositionAgent:
    """
    Agent tạo danh sách topics cho khóa học với skills
    Trả về danh sách topics thay vì lưu trực tiếp vào database
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,
        )
        self.parser = PydanticOutputParser(pydantic_object=CourseAgentResponse)

    def create_system_prompt(self) -> str:
        """Tạo system prompt cho agent"""
        return f"""Bạn là một chuyên gia thiết kế khóa học chuyên nghiệp. Nhiệm vụ của bạn là tạo danh sách topics chi tiết cho khóa học, mỗi topic bao gồm cả danh sách skills mà học viên sẽ đạt được.

NHIỆM VỤ:
1. Phân tích thông tin khóa học được cung cấp
2. Tạo danh sách topics phù hợp với cấp độ và mục tiêu
3. Cho mỗi topic, xác định danh sách skills cụ thể mà học viên sẽ đạt được
4. Ước lượng thời gian hoàn thành toàn bộ khóa học

QUY TẮC THIẾT KẾ TOPICS:
- Topics phải bao quát toàn bộ nội dung khóa học
- Đảm bảo tính logic và liên kết giữa các topics
- Mỗi topic phải có từ 3-7 skills cụ thể và đo lường được
- Skills phải phù hợp với cấp độ khóa học (beginner/intermediate/advanced)
- Độ khó tăng dần qua các topics
- Không vượt quá số lượng topics tối đa được chỉ định

ĐỊNH DẠNG SKILLS:
- Sử dụng động từ hành động: "Hiểu", "Áp dụng", "Phân tích", "Thiết kế", "Triển khai"
- Cụ thể và đo lường được: "Thiết kế thuật toán sắp xếp", không phải "Biết về sắp xếp"
- Phù hợp với ngữ cảnh thực tế

ƯỚC LƯỢNG THỜI GIAN:
- Dựa trên số lượng topics, độ phức tạp và cấp độ
- Đưa ra khoảng thời gian thực tế (VD: "4-6 tuần", "25-30 giờ")

{self.parser.get_format_instructions()}

Lưu ý quan trọng:
- Phải luôn tuân thủ định dạng JSON được yêu cầu
- Không được trả lời lan man hoặc yêu cầu thêm thông tin
- Skills phải thực tế và có thể đạt được thông qua học tập
"""

    def create_user_prompt(self, request: CourseCompositionRequestSchema) -> str:
        """Tạo user prompt với thông tin khóa học"""
        return f"""Hãy tạo danh sách topics chi tiết cho khóa học sau:

**THÔNG TIN KHÓA HỌC:**
- Tiêu đề: {request.course_title}
- Mô tả: {request.course_description}
- Cấp độ: {request.course_level}
- Số topics tối đa: {request.max_topics}
- Số lessons mỗi topic: {request.lessons_per_topic}

**YÊU CẦU:**
1. Tạo danh sách topics phù hợp với nội dung và cấp độ
2. Mỗi topic phải có:
   - Tên topic rõ ràng
   - Mô tả chi tiết nội dung
   - Danh sách prerequisites (nếu có)
   - Danh sách 3-7 skills cụ thể sẽ đạt được
   - Thứ tự hợp lý (order)
3. Ước lượng thời gian hoàn thành toàn bộ khóa học

Hãy tạo kế hoạch học tập toàn diện và thực tế."""

    async def generate_topics(self, request: CourseCompositionRequestSchema) -> CourseAgentResponse:
        """
        Tạo danh sách topics với skills sử dụng LLM
        """
        try:
            system_prompt = self.create_system_prompt()
            user_prompt = self.create_user_prompt(request)

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            logger.info(f"Generating topics for course: {request.course_title}")

            # Gọi LLM để tạo topics
            response = self.llm.invoke(messages)

            # Parse response
            parsed_response = self.parser.parse(response.content)

            # Validate và log kết quả
            logger.info(f"Generated {len(parsed_response.topics)} topics successfully")
            for i, topic in enumerate(parsed_response.topics, 1):
                logger.info(f"Topic {i}: {topic.name} ({len(topic.skills)} skills)")

            return parsed_response

        except Exception as e:
            logger.error(f"Error generating topics: {str(e)}")
            raise Exception(f"Không thể tạo danh sách topics: {str(e)}")

    def act(self, request: CourseCompositionRequestSchema) -> Dict[str, Any]:
        """
        Main method để thực hiện tạo course composition

        Returns:
            Dict chứa danh sách topics với skills và thông tin khóa học
        """
        try:
            # Validate input
            if not request.course_title or not request.course_description:
                raise ValueError("Thiếu thông tin cơ bản của khóa học")

            # Tạo topics với skills
            import asyncio
            result = asyncio.run(self.generate_topics(request))

            # Tạo response theo format mong muốn
            response = CourseCompositionResponseSchema(
                topics=result.topics,
                duration=result.duration,
                status="success"
            )

            logger.info(f"Course composition completed successfully for course: {request.course_title}")
            logger.info(f"Total topics: {len(result.topics)}")
            logger.info(f"Estimated duration: {result.duration}")

            return {
                "status": "success",
                "topics": [topic.model_dump() for topic in result.topics],
                "duration": result.duration,
                "course_id": request.course_id,
                "message": f"Đã tạo {len(result.topics)} topics thành công"
            }

        except Exception as e:
            logger.error(f"Course composition failed: {str(e)}")
            return {
                "status": "error",
                "topics": [],
                "duration": "",
                "course_id": request.course_id,
                "error": str(e),
                "message": f"Lỗi khi tạo khóa học: {str(e)}"
            }
