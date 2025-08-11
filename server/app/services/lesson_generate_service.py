from app.core.agents.lesson_generating_agent_fixed import get_lesson_generating_agent
from app.services.base_generate_service import BaseGenerateService, T


class LessonGenerateService(BaseGenerateService):

    async def generate(self, **kwargs) -> T:
        lesson_generate_agent = get_lesson_generating_agent()
        return await lesson_generate_agent.act(**kwargs)
