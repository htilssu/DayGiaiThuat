"""
Module tracing.py dùng để cấu hình và quản lý tracing với LangSmith.

Module này cung cấp các hàm và tiện ích để thiết lập, cấu hình và sử dụng LangSmith
để theo dõi (tracing) các hoạt động của agent trong ứng dụng.
"""

import os
import asyncio
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from langsmith import Client, traceable
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain_core.callbacks.manager import CallbackManager
from langchain_core.tracers import LangChainTracer

from app.core.config import settings

# Định nghĩa type variable cho decorator
F = TypeVar("F", bound=Callable[..., Any])

# Khởi tạo biến môi trường cho LangSmith nếu chưa được thiết lập
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_API_KEY", settings.LANGSMITH_API_KEY)
os.environ.setdefault("LANGCHAIN_PROJECT", "default")


def get_langsmith_client() -> Client:
    """
    Tạo và trả về một client LangSmith.

    Returns:
        Client: Client LangSmith đã được cấu hình.
    """
    api_key = settings.LANGSMITH_API_KEY
    api_url = "https://api.smith.langchain.com"

    return Client(api_key=api_key, api_url=api_url)


def get_tracer(project_name: Optional[str] = None) -> LangChainTracer:
    """
    Tạo và trả về một LangChain tracer.

    Args:
        project_name: Tên dự án trong LangSmith. Nếu không được cung cấp,
                     sẽ sử dụng giá trị từ biến môi trường.

    Returns:
        LangChainTracer: LangChain tracer đã được cấu hình.
    """
    project = project_name or os.environ.get("LANGCHAIN_PROJECT", "default")
    return LangChainTracer(project_name=project)


def get_callback_manager(project_name: Optional[str] = None) -> CallbackManager:
    """
    Tạo và trả về một callback manager với LangSmith tracer.

    Args:
        project_name: Tên dự án trong LangSmith.

    Returns:
        CallbackManager: CallbackManager với tracer đã được cấu hình.
    """
    tracer = get_tracer(project_name)
    return CallbackManager([tracer])


def trace_agent(
    project_name: Optional[str] = None, tags: Optional[list[str]] = None
) -> Callable[[F], F]:
    """
    Decorator để theo dõi (trace) một hàm hoặc phương thức với LangSmith.

    Args:
        project_name: Tên dự án trong LangSmith.
        tags: Danh sách các tag để gắn với trace.

    Returns:
        Decorator để áp dụng tracing cho hàm hoặc phương thức.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Sử dụng @traceable của langsmith để theo dõi hàm
            traced_func = traceable(
                name=func.__name__,
                project_name=project_name
                or os.environ.get("LANGCHAIN_PROJECT", "default"),
                tags=tags or [],
            )(func)

            try:
                result = await traced_func(*args, **kwargs)
                wait_for_all_tracers()
                return result
            except Exception as e:
                wait_for_all_tracers()
                raise e

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            # Sử dụng @traceable của langsmith để theo dõi hàm
            traced_func = traceable(
                name=func.__name__,
                project_name=project_name
                or os.environ.get("LANGCHAIN_PROJECT", "ai-agent-giai-thuat"),
                tags=tags or [],
            )(func)

            try:
                result = traced_func(*args, **kwargs)
                wait_for_all_tracers()
                return result
            except Exception as e:
                wait_for_all_tracers()
                raise e

        # Chọn wrapper phù hợp dựa trên loại hàm (async hoặc sync)
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator
