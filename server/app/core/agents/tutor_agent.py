from langchain_mongodb import MongoDBChatMessageHistory
from app.core.agents.base_agent import BaseAgent
from langchain.agents import create_tool_calling_agent
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage

from app.core.agents.components.llm_model import create_new_gemini_llm_model
from app.core.config import settings


class TutorAgent(BaseAgent):
    """
    context: context ngữ cảnh hiện tại để llm có thể hiểu được
    """

    def __init__(self):
        super().__init__()
        self.llm_model = create_new_gemini_llm_model()
        self.available_args = ["session_id", "context"]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.agent = create_tool_calling_agent(
            tools=self.tools,
            llm=self.llm_model,
            verbose=True,
            max_retries=3,
            prompt=self.prompt,
        )

    def act(self, *args, **kwargs):

        super().act(*args, **kwargs)

        session_id = kwargs.session_id
        message = kwargs.message
        topic = kwargs.topic

        if not session_id or not message or not topic:
            raise ValueError("Cần cung cấp 'session_id', 'message' và 'topic'.")

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
