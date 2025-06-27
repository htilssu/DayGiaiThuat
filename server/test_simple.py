#!/usr/bin/env python3

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.test_service import TestService
from app.database.database import get_async_session


async def test_api():
    """Test API service để kiểm tra hoạt động của các method mới"""
    async_session_gen = get_async_session()
    session = await async_session_gen.__anext__()

    try:
        service = TestService(session)

        # Test get_user_test_history
        print("Testing get_user_test_history for user_id=2")
        try:
            history = await service.get_user_test_history(2)
            print(f"✅ Found {len(history)} sessions")
            for h in history:
                print(
                    f"  Session: {h.session_id}, Test: {h.test_name}, Score: {h.score}"
                )
        except Exception as e:
            print(f"❌ Error in get_user_test_history: {e}")

        # Test get_test_session_detail
        try:
            session_id = "3359bb89-1ef2-49d9-9eef-a39ace3a7df0"
            print(f"\nTesting get_test_session_detail for session_id={session_id}")
            detail = await service.get_test_session_detail(session_id, 2)
            print(f'✅ Detail: {detail["testName"]}, Status: {detail["status"]}')
        except Exception as e:
            print(f"❌ Error in get_test_session_detail: {e}")

    finally:
        await session.close()


if __name__ == "__main__":
    asyncio.run(test_api())
