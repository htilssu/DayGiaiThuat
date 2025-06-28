from app.core.agents.base_agent import BaseAgent
from app.core.config import settings


class TutorAgent(BaseAgent):
    """
    context: context ngữ cảnh hiện tại để llm có thể hiểu được
    """

    def __init__(self):
        super().__init__()
        self.available_args = ["session_id", "context"]
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
                verbose=True,
                max_retries=3,
                prompt=self.prompt,
            )
        return self._agent

    def act(self, *args, **kwargs):

        super().act(*args, **kwargs)

        session_id = kwargs.session_id
        message = kwargs.message
        topic = kwargs.topic

        if not session_id or not message or not topic:
            raise ValueError("Cần cung cấp 'session_id', 'message' và 'topic'.")

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

        response = runnable.invoke({"input": message})
        print(response.output)


SYSTEM_PROMPT = """
    Bạn là một giảng viên về bộ môn Công nghệ thông tin. Bạn có thể dạy các chủ đề về Công nghệ thông tin.
    Khi người dùng gặp khó khăn, bạn hãy đưa ra các ví dụ thực tế
    giải thích từng bước hoạt động của thuật toán (nếu là thuật toán)
"""
