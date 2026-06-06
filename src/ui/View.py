# Abstract class to build views
from abc import ABC, abstractmethod

class View(ABC):

    @abstractmethod
    def render(self) -> None:
        pass

    @abstractmethod
    def show_error_msg(self, field: str, message: str) -> str:
        pass
