from ..agents.components.llm_model import create_new_llm_model
from app.core.tracing import get_callback_manager


class BaseAgent(object):
    """
    Base class for all agents.
    """

    def __init__(self):
        self.available_args = []
        self._tools = []
        self._base_llm = None
        self._callback_manager = get_callback_manager("default")

    @property
    def base_llm(self):
        """
        Lazy loading cho base_llm

        Returns:
            ChatGoogleGenerativeAI: Instance của model LLM
        """
        if self._base_llm is None:
            self._base_llm = create_new_llm_model()
        return self._base_llm

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
