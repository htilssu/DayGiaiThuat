from ..agents.components.llm_model import create_new_gemini_llm_model


class BaseAgent(object):
    """
    Base class for all agents.
    """

    def __init__(self):
        self.available_args = []
        self.tools = []
        self.base_llm = create_new_gemini_llm_model()

    def act(self, *args, **kwargs):
        self.check_available_args(*args, **kwargs)

    def check_available_args(self, *args, **kwargs):
        """
        Check if the provided arguments are available for the agent.
        """
        for key in kwargs.keys():
            if key not in self.available_args:
                raise TypeError(
                    f"Trong danh sách các tham số cho phép của agent, không tồn tại tham số: {key}"
                )
