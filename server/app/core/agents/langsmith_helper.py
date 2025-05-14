"""
Module langsmith_helper.py cung cấp các tiện ích để làm việc với LangSmith.

Module này chứa các hàm để tạo trace URL, phân tích trace data, và hướng dẫn
về cách sử dụng LangSmith UI để debug và theo dõi agent.
"""

import os
from typing import Dict, Optional

from langsmith import Client

from app.core.config import settings
from app.core.tracing import get_langsmith_client


def get_trace_url(trace_id: str) -> str:
    """
    Tạo URL để truy cập trace trong LangSmith UI.
    
    Args:
        trace_id: ID của trace.
        
    Returns:
        URL tới trace trong LangSmith UI.
    """
    base_url = "https://smith.langchain.com"
    return f"{base_url}/traces/{trace_id}"


def get_recent_traces(project_name: Optional[str] = None, limit: int = 10) -> Dict:
    """
    Lấy các trace gần đây từ LangSmith.
    
    Args:
        project_name: Tên dự án trong LangSmith. Nếu None, sẽ sử dụng
                      giá trị mặc định từ môi trường.
        limit: Số lượng trace tối đa cần lấy.
        
    Returns:
        Dict chứa thông tin về các trace gần đây.
    """
    client = get_langsmith_client()
    project = project_name or os.environ.get("LANGCHAIN_PROJECT", "ai-agent-giai-thuat")
    
    runs = client.list_runs(
        project_name=project,
        execution_order=1,  # Chỉ lấy parent runs
        limit=limit
    )
    
    result = []
    for run in runs:
        result.append({
            "id": run.id,
            "name": run.name,
            "start_time": run.start_time,
            "end_time": run.end_time,
            "status": run.status,
            "url": get_trace_url(run.id),
            "metadata": run.metadata
        })
    
    return {"traces": result}


def get_trace_details(trace_id: str) -> Dict:
    """
    Lấy thông tin chi tiết về một trace cụ thể.
    
    Args:
        trace_id: ID của trace.
        
    Returns:
        Dict chứa thông tin chi tiết về trace.
    """
    client = get_langsmith_client()
    run = client.read_run(trace_id)
    
    # Lấy tất cả các child runs
    child_runs = list(client.list_runs(
        parent_run=trace_id
    ))
    
    child_info = []
    for child in child_runs:
        child_info.append({
            "id": child.id,
            "name": child.name,
            "start_time": child.start_time,
            "end_time": child.end_time,
            "status": child.status,
            "url": get_trace_url(child.id),
            "inputs": child.inputs,
            "outputs": child.outputs,
            "metadata": child.metadata
        })
    
    return {
        "id": run.id,
        "name": run.name,
        "start_time": run.start_time,
        "end_time": run.end_time,
        "status": run.status,
        "url": get_trace_url(run.id),
        "inputs": run.inputs,
        "outputs": run.outputs,
        "metadata": run.metadata,
        "children": child_info
    }


def get_langsmith_usage_guide() -> str:
    """
    Trả về hướng dẫn sử dụng LangSmith UI để theo dõi và debug agent.
    
    Returns:
        Chuỗi văn bản chứa hướng dẫn sử dụng LangSmith UI.
    """
    return """
# Hướng dẫn sử dụng LangSmith để theo dõi Agent

LangSmith là một công cụ mạnh mẽ từ LangChain để theo dõi, debug và cải thiện các ứng dụng AI. Dưới đây là cách sử dụng LangSmith để theo dõi hoạt động của agent trong dự án AI Agent Giải Thuật.

## 1. Truy cập LangSmith Dashboard

Truy cập [LangSmith Dashboard](https://smith.langchain.com/) và đăng nhập với tài khoản của bạn.

## 2. Xem Traces

- Từ dashboard, chọn project "ai-agent-giai-thuat" hoặc "exercise-generator" để xem các trace.
- Mỗi lần agent được gọi, nó sẽ tạo một trace mới trong LangSmith.
- Nhấp vào một trace để xem chi tiết về quá trình thực thi của agent.

## 3. Phân tích Trace

Trong giao diện chi tiết trace, bạn có thể:

- **Timeline View**: Xem thứ tự các hoạt động được thực hiện
- **Trace View**: Xem cấu trúc phân cấp của các bước thực thi
- **Inputs/Outputs**: Xem đầu vào và đầu ra của mỗi bước
- **Prompt Templates**: Xem templates được sử dụng
- **Chat History**: Xem lịch sử tương tác

## 4. Debug với Trace

Khi agent không hoạt động như mong đợi:

1. Kiểm tra các input/output tại mỗi bước để xác định vấn đề
2. Xem có lỗi nào được ghi lại trong trace không
3. Kiểm tra các prompt templates và xem LLM phản hồi như thế nào
4. Phân tích thời gian thực thi của từng bước để tìm điểm nghẽn

## 5. So sánh các Trace

LangSmith cho phép bạn so sánh các trace khác nhau:
1. Chọn hai trace từ danh sách
2. Sử dụng chức năng "Compare" để thấy sự khác biệt

## 6. Đánh giá Hiệu suất 

LangSmith cung cấp các chỉ số về hiệu suất:
1. Thời gian thực thi
2. Tỷ lệ thành công/thất bại
3. Token usage

## 7. Lưu ý về API Calls

Mỗi lần agent thực thi sẽ tạo ra các API calls đến LangSmith:
- Điều này sẽ tính vào hạn ngạch API của bạn
- Trong môi trường sản xuất, bạn có thể muốn giới hạn lượng dữ liệu gửi đến LangSmith

## 8. Khắc phục sự cố

Nếu bạn không thấy trace trong LangSmith:
1. Kiểm tra xem LANGSMITH_API_KEY đã được thiết lập chính xác chưa
2. Đảm bảo các biến môi trường LANGCHAIN_TRACING_V2 và LANGCHAIN_PROJECT đã được thiết lập
3. Kiểm tra log ứng dụng để tìm lỗi liên quan đến LangSmith
    """ 