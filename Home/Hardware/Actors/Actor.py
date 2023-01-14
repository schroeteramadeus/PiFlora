from abc import ABC, abstractmethod

class Actor(ABC):
    __newID = 0
    @abstractmethod
    def __init__(self) -> None:
        self._id = str(Actor.__newID) #type:str
        Actor.__newID += 1

    @abstractmethod
    def Act(self, data):
        #type: (dict[str, object]) -> dict[str, object]
        pass

    @property
    def ID(self):
        #type: () -> str
        return self._id