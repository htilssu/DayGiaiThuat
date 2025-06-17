"""
Module chứa các model của ứng dụng

Thứ tự import rất quan trọng để tránh circular dependency.
"""

# Import các model theo thứ tự phù hợp
from .badge_model import *
from .topic_model import *
from .exercise_model import *
from .course_model import *
from .user_model import *
from .user_state_model import *
from .learning_progress_model import *
from .learning_path_model import *
from .test_model import *
