from typing import TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar("T")


class BaseGenerateService(Generic[T], ABC):
    @abstractmethod
    async def generate(self, **kwargs) -> T:
        raise NotImplementedError("Subclasses must implement generate()")
