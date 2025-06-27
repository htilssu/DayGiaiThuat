"""
Module tracing.py dùng để cấu hình và quản lý tracing với LangSmith.

Module này cung cấp các hàm và tiện ích để thiết lập, cấu hình và sử dụng LangSmith
để theo dõi (tracing) các hoạt động của agent trong ứng dụng.
"""

import os
import asyncio
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, cast

from app.core.config import settings

# Định nghĩa type variable cho decorator
F = TypeVar("F", bound=Callable[..., Any])

# Lazy imports để tăng tốc startup
_langsmith_client = None
_langchain_imports = None


def _get_langchain_imports():
    """Lazy import LangChain components"""
    global _langchain_imports
    if _langchain_imports is None and settings.LANGSMITH_TRACING:
        try:
            from langsmith import Client, traceable
            from langchain.callbacks.tracers.langchain import wait_for_all_tracers
            from langchain_core.callbacks.manager import CallbackManager
            from langchain_core.tracers import LangChainTracer

            _langchain_imports = {
                "Client": Client,
                "traceable": traceable,
                "wait_for_all_tracers": wait_for_all_tracers,
                "CallbackManager": CallbackManager,
                "LangChainTracer": LangChainTracer,
            }
        except ImportError:
            # Nếu không có LangChain, disable tracing
            settings.LANGSMITH_TRACING = False
            _langchain_imports = {}
    return _langchain_imports or {}


# Cấu hình environment variables chỉ khi cần thiết
if settings.LANGSMITH_TRACING:
    if not os.environ.get("LANGSMITH_API_KEY"):
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
    if not os.environ.get("LANGSMITH_PROJECT_NAME"):
        os.environ["LANGSMITH_PROJECT_NAME"] = settings.LANGSMITH_PROJECT


def get_langsmith_client():
    """
    Tạo và trả về một client LangSmith.

    Returns:
        Client: Client LangSmith đã được cấu hình hoặc None.
    """
    global _langsmith_client

    if not settings.LANGSMITH_TRACING:
        return None

    if _langsmith_client is None:
        imports = _get_langchain_imports()
        if not imports:
            return None

        try:
            Client = imports["Client"]
            api_key = settings.LANGSMITH_API_KEY
            api_url = "https://api.smith.langchain.com"
            _langsmith_client = Client(api_key=api_key, api_url=api_url)
        except Exception:
            settings.LANGSMITH_TRACING = False
            return None

    return _langsmith_client


def get_tracer(project_name: Optional[str] = None):
    """
    Tạo và trả về một LangChain tracer.

    Args:
        project_name: Tên dự án trong LangSmith.

    Returns:
        LangChainTracer: LangChain tracer đã được cấu hình hoặc None.
    """
    if not settings.LANGSMITH_TRACING:
        return None

    imports = _get_langchain_imports()
    if not imports:
        return None

    try:
        LangChainTracer = imports["LangChainTracer"]
        project = project_name or os.environ.get("LANGCHAIN_PROJECT", "default")
        return LangChainTracer(project_name=project)
    except Exception:
        return None


def get_callback_manager(project_name: Optional[str] = None):
    """
    Tạo và trả về một callback manager với LangSmith tracer.

    Args:
        project_name: Tên dự án trong LangSmith.

    Returns:
        CallbackManager: CallbackManager với tracer đã được cấu hình.
    """
    if not settings.LANGSMITH_TRACING:
        imports = _get_langchain_imports()
        if imports and "CallbackManager" in imports:
            return imports["CallbackManager"]([])
        return None

    tracer = get_tracer(project_name)
    imports = _get_langchain_imports()

    if tracer and imports and "CallbackManager" in imports:
        return imports["CallbackManager"]([tracer])
    elif imports and "CallbackManager" in imports:
        return imports["CallbackManager"]([])

    return None


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
        # Nếu tracing bị tắt, trả về hàm gốc
        if not settings.LANGSMITH_TRACING:
            return func

        imports = _get_langchain_imports()
        if not imports:
            return func

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                traceable = imports.get("traceable")
                wait_for_all_tracers = imports.get("wait_for_all_tracers")

                if not traceable or not wait_for_all_tracers:
                    return await func(*args, **kwargs)

                # Sử dụng @traceable của langsmith để theo dõi hàm
                traced_func = traceable(
                    name=func.__name__,
                    project_name=project_name or "default",
                    tags=tags or [],
                )(func)

                result = await traced_func(*args, **kwargs)
                wait_for_all_tracers()
                return result
            except Exception as e:
                if "wait_for_all_tracers" in imports:
                    imports["wait_for_all_tracers"]()
                raise e

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                traceable = imports.get("traceable")
                wait_for_all_tracers = imports.get("wait_for_all_tracers")

                if not traceable or not wait_for_all_tracers:
                    return func(*args, **kwargs)

                # Sử dụng @traceable của langsmith để theo dõi hàm
                traced_func = traceable(
                    name=func.__name__,
                    project_name=project_name or "default",
                    tags=tags or [],
                )(func)

                result = traced_func(*args, **kwargs)
                wait_for_all_tracers()
                return result
            except Exception as e:
                if "wait_for_all_tracers" in imports:
                    imports["wait_for_all_tracers"]()
                raise e

        # Chọn wrapper phù hợp dựa trên loại hàm (async hoặc sync)
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        else:
            return cast(F, sync_wrapper)

    return decorator
