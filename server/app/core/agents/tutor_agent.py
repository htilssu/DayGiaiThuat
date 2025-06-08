from langchain_mongodb import MongoDBChatMessageHistory
from app.core.agents.base_agent import BaseAgent
from langchain_core.agents import create_tool_calling_agent
from langchain_core.runnables import RunnableWithMessageHistory

from app.core.agents.components.llm_model import create_new_gemini_llm_model
from server.app.core.config import settings


class TutorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.llm_model = create_new_gemini_llm_model()
        self.available_args = ["session_id"]

        self.agent = create_tool_calling_agent(
            tools=self.tools,
            llm=self.llm_model,
            verbose=True,
            max_retries=3,
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
