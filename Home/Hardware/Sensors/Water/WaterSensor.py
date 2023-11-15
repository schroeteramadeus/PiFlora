from ..Sensor import Sensor
from abc import abstractmethod

WATER_SENSOR_UNDER_WATER = "water"

class WaterSensor(Sensor):
    @abstractmethod
    def PollSensor(self) -> dict[str, object]:
        pass