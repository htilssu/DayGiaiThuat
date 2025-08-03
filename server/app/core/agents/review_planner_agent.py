from typing import override, List, Dict

from app.core.agents.base_agent import BaseAgent
from app.core.agents.components.document_store import get_vector_store
from app.core.agents.components.llm_model import create_new_llm_model
from app.core.config import settings
from app.core.tracing import trace_agent
from app.schemas.exercise_schema import ExerciseDetail

SYSTEM_PROMPT_TEMPLATE = """
Bạn là một chuyên gia phân tích và lập kế hoạch ôn tập, chuyên xác định điểm yếu và kỹ năng cần cải thiện của học sinh để tạo ra kế hoạch ôn tập hiệu quả.

# Nhiệm vụ chính của bạn:
1. Phân tích thông tin về điểm yếu và kỹ năng cần cải thiện của học sinh
2. Xác định các tag kỹ năng cụ thể cần rèn luyện
3. Đề xuất dạng bài tập phù hợp với từng kỹ năng
4. Sử ddụng tool generate_targeted_exercise để tạo bài tập có mục tiêu cụ thể
5. Sử dụng tool analyze_skill_gaps để phân tích khoảng cách kỹ năng

# Quy trình làm việc:
1. Phân tích thông tin đầu vào về điểm yếu và kỹ năng cần cải thiện
2. Sử ddụng analyze_skill_gaps để xác định các kỹ năng cụ thể cần rèn luyện
3. Đề xuất các tag kỹ năng và dạng bài tập tương ứng
4. Sử dụng generate_targeted_exercise để tạo bài tập có mục tiêu

# Các loại kỹ năng cần xem xét:
- Kỹ năng tư duy logic: if-else, switch-case, boolean logic
- Kỹ năng vòng lặp: for, while, nested loops
- Kỹ năng xử lý mảng: array manipulation, searching, sorting
- Kỹ năng xử lý chuỗi: string processing, pattern matching
- Kỹ năng giải thuật cơ bản: recursion, divide and conquer
- Kỹ năng cấu trúc dữ liệu: stack, queue, linked list
- Kỹ năng tối ưu hóa: time complexity, space complexity

# Dạng bài tập tương ứng:
- Bài tập logic: conditional problems, decision trees
- Bài tập vòng lặp: iteration problems, pattern generation
- Bài tập mảng: array manipulation, matrix problems
- Bài tập chuỗi: text processing, string algorithms
- Bài tập đệ quy: recursive problems, tree traversal
- Bài tập cấu trúc dữ liệu: implementation problems
- Bài tập tối ưu: efficiency challenges

Hãy luôn đảm bảo rằng kế hoạch ôn tập được tạo ra có tính cá nhân hóa cao và phù hợp với từng học sinh.
"""

SYSTEM_PROMPT_TEMPLATE_FOR_SKILL_ANALYZER = """
Bạn là chuyên gia phân tích kỹ năng lập trình, hãy phân tích thông tin về điểm yếu và kỹ năng của học sinh để đưa ra đánh giá chi tiết.

Hãy phân tích:
1. Các kỹ năng cụ thể cần cải thiện
2. Mức độ ưu tiên của từng kỹ năng (cao, trung bình, thấp)
3. Đề xuất tag kỹ năng phù hợp
4. Dạng bài tập được khuyến nghị

Trả về kết quả theo format JSON:
{
    "skill_gaps": [
        {
            "skill_name": "tên kỹ năng",
            "priority": "cao/trung bình/thấp",
            "skill_tags": ["tag1", "tag2"],
            "recommended_exercise_types": ["type1", "type2"],
            "description": "mô tả chi tiết về kỹ năng cần cải thiện"
        }
    ],
    "overall_assessment": "đánh giá tổng quan về học sinh",
    "learning_path": "đề xuất lộ trình học tập"
}

{parse_instruction}
"""

SYSTEM_PROMPT_TEMPLATE_FOR_TARGETED_EXERCISE = """
Bạn là chuyên gia tạo bài tập có mục tiêu, hãy tạo bài tập dựa trên skill tags và exercise types được cung cấp.

Hãy đảm bảo bài tập:
1. Tập trung vào kỹ năng cụ thể được yêu cầu
2. Phù hợp với dạng bài tập được đề xuất
3. Có độ khó phù hợp với mức độ học sinh
4. Bao gồm gợi ý hướng dẫn để cải thiện kỹ năng

Hãy trả về kết quả theo đúng format JSON được yêu cầu.

{parse_instruction}
"""


class SkillGapAnalysis:
    def __init__(self):
        self.skill_name: str = ""
        self.priority: str = ""
        self.skill_tags: List[str] = []
        self.recommended_exercise_types: List[str] = []
        self.description: str = ""


class ReviewPlannerAgent(BaseAgent):
    def __init__(
        self,
    ):
        super().__init__()
        self.available_args = ["weaknesses", "skills_to_improve", "session_id", "difficulty_level", "learning_goals"]

        # Vector store để tìm kiếm thông tin về kỹ năng và bài tập
        self.skill_retriever = get_vector_store("document").as_retriever(
            search_kwargs={"k": 3}
        )

        self.exercise_retriever = get_vector_store("exercise").as_retriever(
            search_kwargs={"k": 2}
        )

        self._init_parsers_and_chains()
        self._init_tools()
        self._init_agent()

    def _init_parsers_and_chains(self):
        from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import (
            ChatPromptTemplate,
            MessagesPlaceholder,
            HumanMessagePromptTemplate,
        )

        # Parser cho phân tích kỹ năng
        self.skill_analysis_parser = JsonOutputParser()

        # Parser cho tạo bài tập có mục tiêu
        self.exercise_output_parser = PydanticOutputParser(pydantic_object=ExerciseDetail)

        # Chain phân tích khoảng cách kỹ năng
        self.skill_analysis_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=SYSTEM_PROMPT_TEMPLATE_FOR_SKILL_ANALYZER.format(
                        parse_instruction=self.skill_analysis_parser.get_format_instructions()
                    )
                ),
                MessagesPlaceholder(variable_name="history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

        self.analyze_skill_gaps = self.skill_analysis_prompt | create_new_llm_model(
            top_p=0.8, temperature=0.6
        ) | self.skill_analysis_parser

        # Chain tạo bài tập có mục tiêu
        self.targeted_exercise_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=SYSTEM_PROMPT_TEMPLATE_FOR_TARGETED_EXERCISE.format(
                        parse_instruction=self.exercise_output_parser.get_format_instructions()
                    )
                ),
                MessagesPlaceholder(variable_name="history", optional=True),
                HumanMessagePromptTemplate.from_template("{input}"),
            ]
        )

        self.generate_targeted_exercise = self.targeted_exercise_prompt | create_new_llm_model(
            top_p=0.9, temperature=0.7
        ).with_structured_output(ExerciseDetail)

    def _init_tools(self):
        from langchain_core.tools import Tool

        self.skill_retriever_tool = Tool(
            name="skill_knowledge_retriever",
            func=self.skill_retriever.invoke,
            coroutine=self.skill_retriever.ainvoke,
            description="""Truy xuất thông tin về các kỹ năng lập trình và phương pháp rèn luyện
            từ cơ sở dữ liệu để hỗ trợ việc phân tích và lập kế hoạch ôn tập.""",
        )

        self.exercise_reference_tool = Tool(
            name="exercise_reference_retriever",
            func=self.exercise_retriever.invoke,
            coroutine=self.exercise_retriever.ainvoke,
            description="""Truy xuất thông tin về các bài tập đã có để tham khảo
            dạng bài tập và cách tiếp cận cho từng kỹ năng cụ thể.""",
        )

        self.analyze_skill_gaps_tool = Tool(
            name="analyze_skill_gaps",
            func=self.analyze_skill_gaps.invoke,
            coroutine=self.analyze_skill_gaps.ainvoke,
            description="""Phân tích điểm yếu và kỹ năng cần cải thiện của học sinh,
            trả về danh sách kỹ năng cụ thể với mức độ ưu tiên và đề xuất.""",
        )

        self.generate_targeted_exercise_tool = Tool(
            name="generate_targeted_exercise",
            func=self.generate_targeted_exercise.invoke,
            coroutine=self.generate_targeted_exercise.ainvoke,
            description="""Tạo bài tập có mục tiêu cụ thể dựa trên skill tags và exercise types.
            Đầu vào bao gồm skill_tags, exercise_types, difficulty_level.""",
        )

        self._tools = [
            self.skill_retriever_tool,
            self.exercise_reference_tool,
            self.analyze_skill_gaps_tool,
            self.generate_targeted_exercise_tool,
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
            self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10
        )

    @override
    @trace_agent(project_name="default", tags=["review", "planner", "skill_analysis"])
    async def act(self, *args, **kwargs):
        """
        Phân tích điểm yếu và tạo kế hoạch ôn tập với bài tập có mục tiêu.

        Args:
            weaknesses (str): Mô tả về điểm yếu của học sinh
            skills_to_improve (List[str]): Danh sách kỹ năng cần cải thiện
            session_id (str): ID phiên làm việc
            difficulty_level (str): Mức độ khó của bài tập
            learning_goals (str): Mục tiêu học tập

        Returns:
            Dict: Kết quả phân tích và bài tập được tạo
        """
        super().act(*args, **kwargs)

        weaknesses = kwargs.get("weaknesses", "")
        skills_to_improve = kwargs.get("skills_to_improve", [])
        session_id = kwargs.get("session_id", "")
        difficulty_level = kwargs.get("difficulty_level", "trung bình")
        learning_goals = kwargs.get("learning_goals", "")

        if not session_id:
            raise ValueError("Cần cung cấp 'session_id' để thực hiện phân tích.")

        if not weaknesses and not skills_to_improve:
            raise ValueError("Cần cung cấp thông tin về 'weaknesses' hoặc 'skills_to_improve'.")

        from langchain_core.runnables import RunnableConfig, RunnableWithMessageHistory
        from langchain_mongodb import MongoDBChatMessageHistory

        run_config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={
                "session_id": session_id,
                "weaknesses": weaknesses,
                "skills_to_improve": skills_to_improve,
                "difficulty_level": difficulty_level,
                "agent_type": "review_planner",
            },
            tags=["review", "planner", "skill_analysis", f"session:{session_id}"],
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

        # Tạo input cho agent
        input_text = f"""
        Phân tích và tạo kế hoạch ôn tập dựa trên thông tin sau:
        - Điểm yếu: {weaknesses}
        - Kỹ năng cần cải thiện: {', '.join(skills_to_improve) if skills_to_improve else 'Không xác định'}
        - Mức độ khó: {difficulty_level}
        - Mục tiêu học tập: {learning_goals}
        
        Hãy thực hiện các bước sau:
        1. Phân tích kỹ năng cần cải thiện
        2. Xác định tag kỹ năng và dạng bài tập phù hợp
        3. Tạo bài tập có mục tiêu cụ thể
        """

        try:
            response_from_agent = await agent_with_chat_history.ainvoke(
                {"input": input_text},
                config=run_config,
            )

            if isinstance(response_from_agent, dict):
                return {
                    "success": True,
                    "analysis_result": response_from_agent.get("output"),
                    "session_id": session_id,
                    "metadata": {
                        "weaknesses": weaknesses,
                        "skills_to_improve": skills_to_improve,
                        "difficulty_level": difficulty_level,
                        "learning_goals": learning_goals
                    }
                }
            else:
                raise ValueError("Không thể thực hiện phân tích, đầu ra không hợp lệ.")

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
            }

    async def create_skill_focused_exercises(self, skill_tags: List[str], exercise_types: List[str], difficulty: str = "trung bình") -> List[ExerciseDetail]:
        """
        Tạo nhiều bài tập tập trung vào các kỹ năng cụ thể.

        Args:
            skill_tags: Danh sách tag kỹ năng
            exercise_types: Danh sách dạng bài tập
            difficulty: Mức độ khó

        Returns:
            List[ExerciseDetail]: Danh sách bài tập được tạo
        """
        exercises = []

        for skill_tag, exercise_type in zip(skill_tags, exercise_types):
            try:
                input_data = {
                    "input": f"Tạo bài tập cho kỹ năng: {skill_tag}, dạng bài: {exercise_type}, độ khó: {difficulty}"
                }

                exercise = await self.generate_targeted_exercise.ainvoke(input_data)
                if exercise:
                    exercises.append(exercise)

            except Exception as e:
                print(f"Lỗi khi tạo bài tập cho kỹ năng {skill_tag}: {str(e)}")
                continue

        return exercises
