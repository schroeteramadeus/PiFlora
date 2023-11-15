from abc import ABC, abstractmethod

class Actor(ABC):
    __newID = 0
    @abstractmethod
    def __init__(self) -> None:
        self._id : str = str(Actor.__newID)
        Actor.__newID += 1

    @abstractmethod
    def Act(self, data : dict[str, object]) -> dict[str, object]:
        pass

    @property
    def ID(self) -> str:
        return self._id