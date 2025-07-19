from app.core.agents.base_agent import BaseAgent
from app.core.config import settings
from app.core.tracing import trace_agent


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

        from langchain_core.runnables import RunnableConfig

        run_config = RunnableConfig(
            callbacks=self._callback_manager.handlers,
            metadata={"session_id": session_id, "agent_type": "lesson_generator"},
            tags=["lesson", "generator", f"session:{session_id}"],
        )

        async for chunk in runnable.astream({"input": question,"intermediate_steps": []}, config=run_config):
            # Debug: In ra thông tin chunk để hiểu cấu trúc
            print(f"Chunk type: {type(chunk)}")
            print(
                f"Chunk attributes: {dir(chunk) if hasattr(chunk, '__dict__') else 'No attributes'}"
            )
            print(f"Chunk content: {chunk}")

            # Xử lý chunk data một cách an toàn
            if hasattr(chunk, "content"):
                yield chunk.content
            elif hasattr(chunk, "response"):
                yield chunk.response
            elif hasattr(chunk, "output"):
                yield chunk.output
            elif isinstance(chunk, dict):
                # Nếu chunk là dict, tìm kiếm các key phổ biến
                if "output" in chunk:
                    yield chunk["output"]
                elif "content" in chunk:
                    yield chunk["content"]
                elif "response" in chunk:
                    yield chunk["response"]
                else:
                    # Nếu không tìm thấy key nào, chuyển đổi dict thành string
                    yield str(chunk)
            else:
                # Fallback: chuyển đổi chunk thành string
                yield str(chunk)


SYSTEM_PROMPT = """
    Bạn là một giảng viên về bộ môn Công nghệ thông tin. Bạn có thể dạy các chủ đề về Công nghệ thông tin.
    Khi người dùng gặp khó khăn, bạn hãy đưa ra các ví dụ thực tế
    giải thích từng bước hoạt động của thuật toán (nếu là thuật toán)
"""


def get_tutor_agent():
    """
    Hàm để lấy instance của TutorAgent.
    """
    return TutorAgent()
