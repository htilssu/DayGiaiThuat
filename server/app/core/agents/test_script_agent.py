from app.core.agents.base_agent import BaseAgent


class TestScriptAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.available_args = ["topic_id"]

    def act(self, *args, **kwargs):
        super().act(*args, **kwargs)
