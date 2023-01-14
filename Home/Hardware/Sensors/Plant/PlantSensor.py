import Home.Hardware.Sensors.Sensor as S
from abc import abstractmethod

class PlantSensor(S.Sensor):

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
    