from ..Sensor import Sensor
from abc import abstractmethod

class PlantSensor(Sensor):

    @abstractmethod
    def __init__(self) -> None:
        super().__init__()
        
    @abstractmethod
    def PollSensor(self):
        #type: () -> dict[str, object]
        pass
            
class PlantSensorParameters:
    TEMPERATURE = "temperature"
    BATTERY = "battery"
    MOISTURE = "moisture"
    LIGHT = "light"
    CONDUCTIVITY = "conductivity"
    