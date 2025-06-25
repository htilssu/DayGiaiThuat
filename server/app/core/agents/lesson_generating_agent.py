from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
import json
import re

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.agents.components.llm_model import create_new_creative_llm_model
from app.schemas.lesson_schema import (
    GenerateLessonRequestSchema, CreateLessonSchema, LessonSectionSchema
)


class LessonGeneratingAgent(BaseAgent):
    """
    RAG AI agent that retrieves data from Pinecone and generates lesson content.
    """

    def __init__(self):
        super().__init__()
        self.available_args = [
            "topic_name", "lesson_title", "lesson_description",
            "difficulty_level", "lesson_type", "include_examples",
            "include_exercises", "max_sections"
        ]
        self.vector_store = get_vector_store("document")
        self.llm = create_new_creative_llm_model()
        self.setup_prompts()

    def setup_prompts(self):
        """Setup prompt templates for lesson generation."""

        self.lesson_structure_prompt = PromptTemplate(
            input_variables=[
                "topic_name", "lesson_title", "lesson_description",
                "difficulty_level", "lesson_type", "context", "max_sections"
            ],
            template="""
            Bạn là một chuyên gia giáo dục về lập trình và giải thuật. Dựa trên thông tin sau, hãy tạo cấu trúc bài học:

            Chủ đề: {topic_name}
            Tiêu đề bài học: {lesson_title}
            Mô tả: {lesson_description}
            Độ khó: {difficulty_level}
            Loại bài học: {lesson_type}
            Số phần tối đa: {max_sections}

            Thông tin tham khảo từ cơ sở dữ liệu:
            {context}

            Hãy tạo cấu trúc bài học với các phần sau (trả về JSON):
            {{
                "sections": [
                    {{
                        "type": "text|code|quiz",
                        "title": "Tiêu đề phần",
                        "description": "Mô tả ngắn về nội dung",
                        "order": 1
                    }}
                ]
            }}

            Lưu ý:
            - Bắt đầu với phần giới thiệu (type: "text")
            - Bao gồm các ví dụ code nếu cần thiết (type: "code")
            - Kết thúc với bài tập hoặc câu hỏi (type: "quiz")
            - Đảm bảo logic và thứ tự hợp lý
            """
        )

        self.content_generation_prompt = PromptTemplate(
            input_variables=["section_info", "context", "difficulty_level"],
            template="""
            Dựa trên thông tin phần bài học và ngữ cảnh, hãy tạo nội dung chi tiết:

            Thông tin phần: {section_info}
            Độ khó: {difficulty_level}
            Ngữ cảnh tham khảo: {context}

            Tạo nội dung phù hợp với loại phần:
            - text: Nội dung lý thuyết rõ ràng, dễ hiểu
            - code: Ví dụ code với giải thích chi tiết
            - quiz: Câu hỏi trắc nghiệm với 4 lựa chọn và giải thích

            Trả về JSON:
            {{
                "content": "Nội dung chi tiết",
                "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}} (chỉ cho quiz),
                "answer": 0-3 (chỉ cho quiz, 0=A, 1=B, 2=C, 3=D),
                "explanation": "Giải thích đáp án" (chỉ cho quiz)
            }}
            """
        )

    def retrieve_relevant_context(self, query: str, k: int = 5) -> str:
        """
        Retrieve relevant documents from Pinecone vector store.
        """
        try:
            # Use contextual compression for better retrieval
            compressor = LLMChainExtractor.from_llm(self.llm)
            compression_retriever = ContextualCompressionRetriever(
                base_retriever=self.vector_store.as_retriever(search_kwargs={"k": k}),
                base_compressor=compressor
            )

            docs = compression_retriever.get_relevant_documents(query)

            # Combine all retrieved content
            context_parts = []
            for doc in docs:
                if hasattr(doc, 'page_content'):
                    context_parts.append(doc.page_content)
                elif isinstance(doc, dict) and 'page_content' in doc:
                    context_parts.append(doc['page_content'])

            return "\n\n".join(context_parts) if context_parts else "Không tìm thấy thông tin liên quan."

        except Exception as e:
            print(f"Error retrieving context: {e}")
            return "Không thể truy xuất thông tin từ cơ sở dữ liệu."

    def generate_lesson_structure(self, request: GenerateLessonRequestSchema, context: str) -> List[Dict[str, Any]]:
        """
        Generate lesson structure based on retrieved context.
        """
        try:
            chain = LLMChain(llm=self.llm, prompt=self.lesson_structure_prompt)

            response = chain.run(
                topic_name=request.topic_name,
                lesson_title=request.lesson_title,
                lesson_description=request.lesson_description,
                difficulty_level=request.difficulty_level,
                lesson_type=request.lesson_type,
                context=context,
                max_sections=request.max_sections
            )

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                structure_data = json.loads(json_match.group())
                return structure_data.get("sections", [])
            else:
                # Fallback: create basic structure
                return [
                    {"type": "text", "title": "Giới thiệu", "description": "Phần mở đầu", "order": 1},
                    {"type": "text", "title": "Nội dung chính", "description": "Nội dung bài học", "order": 2},
                    {"type": "quiz", "title": "Bài tập", "description": "Câu hỏi kiểm tra", "order": 3}
                ]

        except Exception as e:
            print(f"Error generating lesson structure: {e}")
            return []

    def generate_section_content(self, section_info: Dict[str, Any], context: str, difficulty_level: str) -> Dict[str, Any]:
        """
        Generate detailed content for a lesson section.
        """
        try:
            chain = LLMChain(llm=self.llm, prompt=self.content_generation_prompt)

            response = chain.run(
                section_info=json.dumps(section_info, ensure_ascii=False),
                context=context,
                difficulty_level=difficulty_level
            )

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                content_data = json.loads(json_match.group())
                return content_data
            else:
                # Fallback content
                return {
                    "content": (
                        f"Nội dung cho phần: "
                        f"{section_info.get('title', 'Không có tiêu đề')}"
                    ),
                    "options": None,
                    "answer": None,
                    "explanation": None
                }

        except Exception as e:
            print(f"Error generating section content: {e}")
            return {
                "content": (
                    f"Lỗi khi tạo nội dung cho phần: "
                    f"{section_info.get('title', 'Không có tiêu đề')}"
                ),
                "options": None,
                "answer": None,
                "explanation": None
            }

    def generate_lesson(self, request: GenerateLessonRequestSchema) -> CreateLessonSchema:
        """
        Main method to generate a complete lesson using RAG.
        """
        # Validate input
        self.check_available_args(**request.dict())

        # Retrieve relevant context from Pinecone
        query = f"{request.topic_name} {request.lesson_title} {request.lesson_description}"
        context = self.retrieve_relevant_context(query)

        # Generate lesson structure
        structure = self.generate_lesson_structure(request, context)

        # Generate content for each section
        sections = []
        for section_info in structure:
            content_data = self.generate_section_content(
                section_info, context, request.difficulty_level
            )

            section = LessonSectionSchema(
                type=section_info.get("type", "text"),
                content=content_data.get("content", ""),
                order=section_info.get("order", len(sections) + 1),
                options=content_data.get("options"),
                answer=content_data.get("answer"),
                explanation=content_data.get("explanation")
            )
            sections.append(section)

        # Create lesson schema
        lesson = CreateLessonSchema(
            external_id=(
                f"lesson_{request.topic_name.lower().replace(' ', '_')}_{len(sections)}"
            ),
            title=request.lesson_title,
            description=request.lesson_description,
            topic_id=0,  # This should be set by the caller
            order=1,     # This should be set by the caller
            sections=sections
        )

        return lesson

    def act(self, request: GenerateLessonRequestSchema) -> CreateLessonSchema:
        """
        Execute the lesson generation process.
        """
        return self.generate_lesson(request)
