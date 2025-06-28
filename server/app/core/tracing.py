"""
Module tracing.py dùng để cấu hình và quản lý tracing với LangSmith.

Module này cung cấp các hàm và tiện ích để thiết lập, cấu hình và sử dụng LangSmith
để theo dõi (tracing) các hoạt động của agent trong ứng dụng.
"""

import functools
import os
from typing import Any, Callable, Dict, List, Optional

from app.core.config import settings

# Global cache cho imports
_langchain_imports = None
_langsmith_client = None


def _get_langchain_imports():
    """
    Import các module LangChain/LangSmith cần thiết với lazy loading.

    Returns:
        Dict[str, Any]: Dictionary chứa các imported classes hoặc None.
    """
    global _langchain_imports

    if _langchain_imports is not None:
        return _langchain_imports

    if not settings.LANGSMITH_TRACING:
        _langchain_imports = {}
        return _langchain_imports

    try:
        # Lazy import - chỉ import khi cần thiết
        from langsmith import Client
        from langchain.callbacks.tracers import LangChainTracer

        _langchain_imports = {"Client": Client, "LangChainTracer": LangChainTracer}
        return _langchain_imports

    except ImportError:
        # Nếu không thể import, tắt tracing và cache kết quả rỗng
        settings.LANGSMITH_TRACING = False
        _langchain_imports = {}
        return _langchain_imports


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


def get_callback_manager(project_name: str = "default"):
    """
    Tạo và trả về một CallbackManager với tracer được cấu hình.

    Args:
        project_name: Tên dự án LangSmith.

    Returns:
        CallbackManager: Callback manager với tracer hoặc None nếu tracing bị tắt.
    """
    if not settings.LANGSMITH_TRACING:
        return None

    try:
        # Lazy import - chỉ import khi cần thiết
        from langchain.callbacks import CallbackManager

        tracer = get_tracer(project_name)
        if tracer:
            return CallbackManager([tracer])
        else:
            return CallbackManager([])

    except ImportError:
        # Nếu không thể import LangChain callbacks, trả về None
        return None
    except Exception:
        # Nếu có lỗi khác, trả về None
        return None


def trace_agent(
    project_name: str = "default",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Callable:
    """
    Decorator để trace hoạt động của agent với LangSmith.

    Args:
        project_name: Tên dự án LangSmith.
        tags: Danh sách tags cho việc trace.
        metadata: Metadata bổ sung cho việc trace.

    Returns:
        Callable: Decorated function.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not settings.LANGSMITH_TRACING:
                return await func(*args, **kwargs)

            tracer = get_tracer(project_name)
            if not tracer:
                return await func(*args, **kwargs)

            # Thêm tracer vào callback manager nếu có
            try:
                # Lazy import cho LangChain callbacks
                from langchain.callbacks import CallbackManager

                instance = args[0] if args else None
                if hasattr(instance, "_callback_manager"):
                    if not instance._callback_manager:
                        instance._callback_manager = CallbackManager([tracer])
                    else:
                        instance._callback_manager.add_handler(tracer)

                return await func(*args, **kwargs)
            except ImportError:
                # Fallback nếu không có LangChain callbacks
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"Lỗi tracing: {e}")
                return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not settings.LANGSMITH_TRACING:
                return func(*args, **kwargs)

            tracer = get_tracer(project_name)
            if not tracer:
                return func(*args, **kwargs)

            try:
                # Lazy import cho LangChain callbacks
                from langchain.callbacks import CallbackManager

                instance = args[0] if args else None
                if hasattr(instance, "_callback_manager"):
                    if not instance._callback_manager:
                        instance._callback_manager = CallbackManager([tracer])
                    else:
                        instance._callback_manager.add_handler(tracer)

                return func(*args, **kwargs)
            except ImportError:
                # Fallback nếu không có LangChain callbacks
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Lỗi tracing: {e}")
                return func(*args, **kwargs)

        # Kiểm tra xem function có phải async không
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
