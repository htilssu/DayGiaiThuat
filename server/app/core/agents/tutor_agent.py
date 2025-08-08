from app.core.agents.base_agent import BaseAgent
from app.core.config import settings
from app.core.tracing import trace_agent
from app.models.lesson_model import Lesson
from app.utils.model_utils import model_to_dict
from langchain_core.agents import AgentFinish
from langchain_core.tools import Tool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TutorAgent(BaseAgent):

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.available_args = ["session_id", "question", "type", "context_id"]
        self._prompt = None
        self.db = db
        self._agent = None

    @property
    def tools(self):
        if self._tools is None:

            self._tools = [
                Tool(
                    name="get_context",
                    func=self.get_context,
                    description="Lấy context người dùng đang học dựa vào context_id và type.",
                )
            ]
        return self._tools

    @property
    def prompt(self):
        if self._prompt is None:
            from langchain_core.messages import SystemMessage
            from langchain_core.prompts import (
                ChatPromptTemplate,
                HumanMessagePromptTemplate,
                MessagesPlaceholder,
            )

            self._prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    MessagesPlaceholder(variable_name="history", optional=True),
                    HumanMessagePromptTemplate.from_template("{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
        return self._prompt

    async def get_context(self, context_id, context_type):
        if not context_id or not context_type:
            raise ValueError("Cần cung cấp 'context_id' và 'type'.")

        if context_type not in ["lesson", "exercise"]:
            raise ValueError("Type phải là 'lesson' hoặc 'exercise'.")

        if context_type == "lesson":
            context = await self.db.execute(
                select(Lesson).where(Lesson.id == context_id)
            )
            context = context.scalar_one_or_none()
            if not context:
                raise ValueError(f"Không tìm thấy lesson với id {context_id}.")
            return model_to_dict(context)
        elif context_type == "exercise":
            from app.models.exercise_model import Exercise

            context = await self.db.execute(
                select(Exercise).where(Exercise.id == context_id)
            )
            context = context.scalar_one_or_none()
            if not context:
                raise ValueError(f"Không tìm thấy exercise với id {context_id}.")
            return model_to_dict(context)
        return None

    @property
    def agent(self):
        if self._agent is None:
            from langchain.agents import create_tool_calling_agent

            self._agent = create_tool_calling_agent(
                tools=self.tools,
                llm=self.base_llm,
                prompt=self.prompt,
            )
        return self._agent

    def act(self, *args, **kwargs):

        super().act(*args, **kwargs)

        session_id = kwargs.get("session_id")
        question = kwargs.get("question")

        if not session_id or not question:
            raise ValueError("Cần cung cấp 'session_id' và 'question'.")

        # Lazy import - chỉ import khi cần thiết
        from langchain_core.runnables import RunnableWithMessageHistory
        from langchain_mongodb import MongoDBChatMessageHistory

        runnable = RunnableWithMessageHistory(
            self.agent,
            history_messages_key="history",
            get_session_history=lambda: MongoDBChatMessageHistory(
                settings.MONGO_URI,
                session_id,
            ),
        )

        response = runnable.invoke({"input": question})
        print(response.output)

    @trace_agent("tutor_agent.act_stream")
    async def act_stream(self, *args, **kwargs):
        super().act(*args, **kwargs)

        session_id = kwargs.get("session_id")
        question = kwargs.get("question")

        if not session_id or not question:
            raise ValueError("Cần cung cấp 'session_id' và 'question'.")

        from langchain_core.runnables import RunnableWithMessageHistory
        from langchain_mongodb import MongoDBChatMessageHistory

        runnable = RunnableWithMessageHistory(
            self.agent,
            history_messages_key="history",
            get_session_history=lambda: MongoDBChatMessageHistory(
                settings.MONGO_URI,
                session_id,
            ),
        )

        from langchain_core.runnables import RunnableConfig

        run_config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={"session_id": session_id, "agent_type": "lesson_generator"},
            tags=["lesson", "generator", f"session:{session_id}"],
        )

        async for chunk in runnable.astream(
            {"input": question, "intermediate_steps": []}, config=run_config
        ):
            if chunk and isinstance(chunk, AgentFinish):
                yield chunk.return_values.get("output", "")

            elif chunk and isinstance(chunk, str):
                yield chunk


SYSTEM_PROMPT = """
    Bạn là một giảng viên về bộ môn Công nghệ thông tin. Bạn có thể dạy các chủ đề về Công nghệ thông tin.
    Nếu history không có context về ngữ cảnh, hãy gọi tool để lấy context người dùng đang học dựa vào context_id, type.
    Khi người dùng gặp khó khăn, bạn hãy đưa ra các ví dụ thực tế
    giải thích từng bước hoạt động của thuật toán (nếu là thuật toán)
    Tên của bạn là Alex, có thể xưng với sinh viên là "thầy", thầy Alex đang công tác tại công ty AGT - Học thuật toán và lập trình.
    Bạn sẽ trả lời câu hỏi của sinh viên một cách chi tiết và dễ hiểu nhất.
    Nếu bạn không biết câu trả lời, hãy nói rằng bạn không biết và sẽ tìm hiểu
"""
