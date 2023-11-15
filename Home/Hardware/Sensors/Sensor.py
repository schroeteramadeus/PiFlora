from abc import ABC, abstractmethod

class Sensor(ABC):
    __newID : int = 0
    @abstractmethod
    def __init__(self) -> None:
        self._id : str = str(Sensor.__newID)
        Sensor.__newID += 1
    
    @abstractmethod
    def PollSensor(self) -> dict[str, object]:
        pass

    @property
    def ID(self) -> str:
        return self._id