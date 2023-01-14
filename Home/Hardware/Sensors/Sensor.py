from abc import ABC, abstractmethod

class Sensor(ABC):
    __newID = 0
    @abstractmethod
    def __init__(self) -> None:
        self._id = str(Sensor.__newID)#type:str
        Sensor.__newID += 1
    @abstractmethod
    def PollSensor(self):
        #type: () -> dict[str, object]
        pass

    @property
    def ID(self):
        #type: () -> str
        return self._id