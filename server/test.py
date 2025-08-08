import asyncio
from app.core.agents.test_generate_agent import get_input_test_agent


async def main():
    ip_ag = get_input_test_agent()
    await ip_ag.act(course_id=215)


if __name__ == "__main__":
    asyncio.run(main())
