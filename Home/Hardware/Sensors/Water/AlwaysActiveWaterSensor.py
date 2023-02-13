from .WaterSensor import WaterSensor, WATER_SENSOR_UNDER_WATER

class AlwaysActiveWaterSensor(WaterSensor):

    def __init__(self) -> None:
        #type: () -> None
        pass

    def PollSensor(self):
        #type: () -> dict[str, object]

        return {
                WATER_SENSOR_UNDER_WATER: True
            }