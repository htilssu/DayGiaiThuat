"""
Module agent_tracing.py cung cấp các API endpoint để truy cập dữ liệu tracing.

Module này cung cấp các API endpoint để truy cập thông tin về các trace, 
hiển thị thông tin debug và phân tích hiệu suất agent từ LangSmith.
"""

from typing import Dict, Optional, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.agents.langsmith_helper import (
    get_langsmith_usage_guide,
    get_recent_traces,
    get_trace_details
)

router = APIRouter(
    prefix="/agent-tracing",
    tags=["agent-tracing"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.get("/guide")
async def get_usage_guide() -> Dict[str, str]:
    """
    Trả về hướng dẫn sử dụng LangSmith UI để theo dõi agent.
    
    Returns:
        Dict chứa hướng dẫn sử dụng.
    """
    guide = get_langsmith_usage_guide()
    return {"guide": guide}


@router.get("/traces")
async def list_traces(
    project_name: Optional[str] = None,
    limit: int = 10
) -> Dict[str, List[Dict]]:
    """
    Lấy danh sách các trace gần đây từ LangSmith.
    
    Args:
        project_name: Tên dự án trong LangSmith.
        limit: Số lượng trace tối đa cần lấy.
        
    Returns:
        Dict chứa danh sách các trace.
        
    Raises:
        HTTPException: Nếu có lỗi khi lấy danh sách trace.
    """
    try:
        return get_recent_traces(project_name, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy danh sách trace: {str(e)}"
        )


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str) -> Dict:
    """
    Lấy thông tin chi tiết về một trace cụ thể.
    
    Args:
        trace_id: ID của trace.
        
    Returns:
        Dict chứa thông tin chi tiết về trace.
        
    Raises:
        HTTPException: Nếu không tìm thấy trace hoặc có lỗi khi lấy thông tin.
    """
    try:
        return get_trace_details(trace_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy trace hoặc có lỗi: {str(e)}"
        ) 