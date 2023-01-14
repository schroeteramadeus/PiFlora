import Home.Hardware.Sensors.Sensor as S
from abc import abstractmethod

WATER_SENSOR_UNDER_WATER = "water"

class WaterSensor(S.Sensor):
    @abstractmethod
    def PollSensor(self):
        #type: () -> dict[str, object]
        pass