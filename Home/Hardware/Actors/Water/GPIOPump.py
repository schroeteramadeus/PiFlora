from .Pump import Pump
from ...GPIOManager import GPIOManager, GPIO, _GPIOHandle, GPIOTypes

class GPIOPump(Pump):

    #TODO Create SafetyPump class with FAILSAFE: if last_time_watered > threshold, maximumWaterInOneSession = 100ml
    def __init__(self, gpio : GPIO) -> None:
        super().__init__()
        self._id : str = str(gpio.Port)
        self.__gpio : GPIO = gpio
        self.__gpioHandle :_GPIOHandle = None

        found = False
        for g in GPIOManager.GetAvailableGPIOs():
            if g.Port == gpio.Port and gpio.Type == g.Type and g.Type == GPIOTypes.STANDARDINOUT:
                self.__gpioHandle = GPIOManager.RequestGPIO(gpio)
                found = True
                break

        if not found:
            raise AttributeError("GPIO Pin " + str(gpio.Port) + " not available or wrong type (got: " + str(g.Type) + ", needed: " + str(GPIOTypes.STANDARDINOUT) + ")")

    def __del__(self):
        GPIOManager.FreeGPIO(self.__gpioHandle)

    def GPIO(self) -> GPIO:
        return self.__gpio

    def Water(self, ml : float) -> float:
        #TODO use gpio handle for hardware interaction
        return ml