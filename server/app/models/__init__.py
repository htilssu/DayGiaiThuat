"""
Module chứa các model của ứng dụng

Thứ tự import rất quan trọng để tránh circular dependency.
"""

# Import các model theo thứ tự phù hợp
from .badge import *
from .topic import *
from .exercise import *
from .course import *
from .user import *
from .user_state import *
from .learning_progress import *
from .learning_path import *
from .test import *
