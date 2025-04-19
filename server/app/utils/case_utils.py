"""
Utility functions để xử lý chuyển đổi định dạng snake_case và camelCase
"""

import re
from typing import Any, Dict, List, Union

def to_camel_case(snake_str: str) -> str:
    """
    Chuyển đổi string từ snake_case sang camelCase
    
    Args:
        snake_str: String ở dạng snake_case
        
    Returns:
        String ở dạng camelCase
    """
    # Xử lý các trường hợp đặc biệt như chuỗi rỗng
    if not snake_str:
        return snake_str
        
    # Chuyển đổi từ snake_case sang camelCase
    components = snake_str.split('_')
    # Giữ nguyên thành phần đầu tiên và chuyển các thành phần tiếp theo sang dạng title
    return components[0] + ''.join(x.title() for x in components[1:])

def to_snake_case(camel_str: str) -> str:
    """
    Chuyển đổi string từ camelCase sang snake_case
    
    Args:
        camel_str: String ở dạng camelCase
        
    Returns:
        String ở dạng snake_case
    """
    # Xử lý các trường hợp đặc biệt như chuỗi rỗng
    if not camel_str:
        return camel_str
    
    # Sử dụng regex để tách các từ bắt đầu bằng chữ hoa
    # Đầu tiên thay thế chữ cái viết hoa (không phải đầu chuỗi) với '_' và chữ đó
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    # Tiếp theo xử lý các chữ cái viết hoa liên tiếp
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def convert_dict_to_camel_case(obj: Any) -> Any:
    """
    Chuyển đổi đệ quy tất cả các key trong dictionary từ snake_case sang camelCase
    
    Args:
        obj: Đối tượng cần chuyển đổi (dict, list hoặc giá trị cơ bản)
        
    Returns:
        Đối tượng với các key đã chuyển sang camelCase
    """
    if isinstance(obj, dict):
        new_dict: Dict[str, Any] = {}
        for key, value in obj.items():
            # Chuyển đổi key sang camelCase
            new_key = to_camel_case(key)
            # Chuyển đổi đệ quy value
            new_dict[new_key] = convert_dict_to_camel_case(value)
        return new_dict
    elif isinstance(obj, list):
        # Xử lý từng phần tử trong danh sách
        return [convert_dict_to_camel_case(item) for item in obj]
    else:
        # Trả về nguyên giá trị nếu không phải dict hoặc list
        return obj

def convert_dict_to_snake_case(obj: Any) -> Any:
    """
    Chuyển đổi đệ quy tất cả các key trong dictionary từ camelCase sang snake_case
    
    Args:
        obj: Đối tượng cần chuyển đổi (dict, list hoặc giá trị cơ bản)
        
    Returns:
        Đối tượng với các key đã chuyển sang snake_case
    """
    if isinstance(obj, dict):
        new_dict: Dict[str, Any] = {}
        for key, value in obj.items():
            # Chuyển đổi key sang snake_case
            new_key = to_snake_case(key)
            # Chuyển đổi đệ quy value
            new_dict[new_key] = convert_dict_to_snake_case(value)
        return new_dict
    elif isinstance(obj, list):
        # Xử lý từng phần tử trong danh sách
        return [convert_dict_to_snake_case(item) for item in obj]
    else:
        # Trả về nguyên giá trị nếu không phải dict hoặc list
        return obj