from app.core.agents.base_agent import BaseAgent
from app.core.config import settings
from app.core.tracing import trace_agent
from langchain_core.agents import AgentFinish


class TutorAgent(BaseAgent):
    """
    context: context ngữ cảnh hiện tại để llm có thể hiểu được
    """

    def __init__(self):
        super().__init__()
        self.available_args = ["session_id", "question", "type", "context_id"]
        self._prompt = None
        self._agent = None

    @property
    def prompt(self):
        """Lazy initialization của prompt template"""
        if self._prompt is None:
            # Lazy import - chỉ import khi cần thiết
            from langchain_core.prompts import (
                ChatPromptTemplate,
                HumanMessagePromptTemplate,
                MessagesPlaceholder,
            )
            from langchain_core.messages import SystemMessage

            self._prompt = ChatPromptTemplate.from_messages(
                [
                    SystemMessage(content=SYSTEM_PROMPT),
                    MessagesPlaceholder(variable_name="history", optional=True),
                    HumanMessagePromptTemplate.from_template("{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )
        return self._prompt

    @property
    def agent(self):
        """Lazy initialization của agent"""
        if self._agent is None:
            # Lazy import - chỉ import khi cần thiết
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


def get_tutor_agent():
    """
    Hàm để lấy instance của TutorAgent.
    """
    return TutorAgent()
