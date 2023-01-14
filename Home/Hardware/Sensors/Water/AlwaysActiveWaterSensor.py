import Home.Hardware.Sensors.Water.WaterSensor as WS

class AlwaysActiveWaterSensor:
    def PollSensor(self):
        #type: () -> dict[str, object]

        return {
                WS.WATER_SENSOR_UNDER_WATER: True
            }