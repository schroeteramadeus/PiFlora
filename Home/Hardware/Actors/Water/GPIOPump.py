import Home.Hardware.Actors.Water.Pump as P
from Home.Hardware.GPIOManager import GPIOManager, GPIO, _GPIOHandle, GPIOTypes
class GPIOPump(P.Pump):

    #TODO Create SafetyPump class with FAILSAFE: if last_time_watered > threshold, maximumWaterInOneSession = 100ml
    def __init__(self, gpio) -> None:
        #type: (GPIO) -> None
        super().__init__()
        self._id = str(gpio.Port) #type: str
        self.__gpio = gpio #type: GPIO
        self.__gpioHandle = None #type: _GPIOHandle

        for g in GPIOManager.GetAvailableGPIOs():
            if g.Port == gpio.Port and  g.Type == GPIOTypes.STANDARDINOUT:
                self.__gpioHandle = GPIOManager.RequestGPIO(gpio)
                break
        else:
            raise AttributeError("GPIO Pin " + gpio + " not available")

    def __del__(self):
        GPIOManager.FreeGPIO(self.__gpioHandle)

    def GPIO(self):
        #type: () -> GPIO
        return self.__gpio

    def Water(self, ml):
        #type: (float) -> float
        #TODO use gpio handle for hardware interaction
        return ml