from .WaterSensor import WaterSensor, WATER_SENSOR_UNDER_WATER
import time

class VirtualWaterSensor(WaterSensor):

    def __init__(self, maximumWater : float, minimumWater : float, waterPerDay : float) -> None:
        super().__init__()
        self.__maximumWater = maximumWater
        self.__minimumWater = minimumWater
        self.__waterPerDay = waterPerDay
        self.__lastTimeFilled = time.time()

    def PollSensor(self) -> dict[str, object]:
        waterPerSecond = self.__waterPerDay / 24 / 60 / 60
        secondsSinceRefill = time.time() - self.__lastTimeFilled

        waterLeft = self.__maximumWater - (waterPerSecond * secondsSinceRefill)

        if waterLeft  > self.__minimumWater:
            return {
                WATER_SENSOR_UNDER_WATER: True
            }
        else:
            return {
                WATER_SENSOR_UNDER_WATER: False
            }

    def Reset(self) -> None:
        self.__lastTimeFilled = time.time()