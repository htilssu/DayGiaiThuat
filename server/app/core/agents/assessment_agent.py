from typing import override
from langchain_core.agents import BaseAgent

from app.core.tracing import trace_agent


class AssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    @override
    @trace_agent(project_name="default", tags=["assessment"])
    def act(self, *args, **kwargs):
        super().act(*args, **kwargs)
