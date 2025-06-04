from typing import overload


class BaseAgent(object):
    """
    Base class for all agents.
    """

    def __init__(self):
        self.available_args = []

    def act(self, *args, **kwargs):
        self.check_available_args(*args, **kwargs)

    def check_available_args(self, *args, **kwargs):
        """
        Check if the provided arguments are available for the agent.
        """
        for key in kwargs.keys():
            if key not in self.available_args:
                raise TypeError(f"Unknown argument: {key}")
