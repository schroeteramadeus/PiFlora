#import os
#os.uname()[4].startswith("arm")

# # GPIO-Bibliothek laden
# import RPi.GPIO as GPIO

# # BCM-Nummerierung verwenden
# GPIO.setmode(GPIO.BCM)

# # GPIO 17 (Pin 11) als Ausgang setzen
# GPIO.setup(17, GPIO.OUT)

# # GPIO 17 (Pin 11) auf HIGH setzen
# GPIO.output(17, True)

# # GPIO 17 (Pin 11) auf LOW setzen
# GPIO.output(17, false)

# # GPIO 18 (Pin 12) als Eingang setzen
# GPIO.setup(18, GPIO.IN)

# # GPIO 18 (Pin 12) lesen und ausgeben
# print (GPIO.input(18))

# # Benutzte GPIOs freigeben
# GPIO.cleanup()

import logging


logger = logging.getLogger(__name__)

class _GPIOType:
    def __init__(self, name) -> None:
        #type: (str) -> None
        self.__name = name
    
    @property
    def Name(self):
        #type: () -> str
        return self.__name


class GPIOTypes:
    STANDARDINOUT = _GPIOType("standardinout")

    def GetAll():
        return [
            GPIOTypes.STANDARDINOUT,
        ]

class GPIO:
    def __init__(self, port, type) -> None:
        #type: (int, _GPIOType) -> None
        self.__port = port
        self.__type = type

    @property
    def Port(self):
        #type: () -> int
        return self.__port

    @property
    def Type(self):
        #type: () -> _GPIOType
        return self.__type

class _GPIOHandle:
    def __init__(self, gpio) -> None:
        #type: (GPIO) -> None
        self.__gpio = gpio

    @property
    def GPIO(self):
        #type: () -> GPIO
        return self.__gpio

    def Write(self, value):
        #type: (bool) -> None
        #TODO if writeable
        pass
    def Read(self):
        #type: () -> bool
        #TODO if writeable
        pass
    


class GPIOManager:

    #TODO
    #maybe use pinout()?
    __GPIOs = { #type: dict[GPIO, bool]
        GPIO(17, GPIOTypes.STANDARDINOUT) : False
    }

    def GetAvailableGPIOs():
        #type: () -> list[GPIO]
        unusedGPIOs = []
        for gpio in GPIOManager.__GPIOs:
            if not GPIOManager.__GPIOs[gpio]:
                unusedGPIOs.append(gpio)

        return unusedGPIOs

    def GetAllGPIOs():
        #type: () -> list[GPIO]
        return list(GPIOManager.__GPIOs.keys())

    def GetFilteredGPIOs(type):
        #type: (_GPIOType) -> list[GPIO]
        output = []
        availableGPIOs = GPIOManager.GetAllGPIOs()
        for gpio in availableGPIOs:
            if gpio.Type == type:
                output.append(gpio)
        return output

    def GetFilteredAvailableGPIOs(type):
        #type: (_GPIOType) -> list[GPIO]
        output = []
        availableGPIOs = GPIOManager.GetAvailableGPIOs()
        for gpio in availableGPIOs:
            if gpio.Type == type:
                output.append(gpio)
        return output

    def RequestGPIO(gpio):
        #type: (GPIO) -> _GPIOHandle
        if gpio in GPIOManager.GetAvailableGPIOs():
            logger.info("Binding GPIO " + str(gpio.Port))
            handle = _GPIOHandle(gpio)
            return handle
        else:
            raise AttributeError("GPIO" + str(gpio.Port) + " not valid")

    def FreeGPIO(gpioHandle):
        #type: (_GPIOHandle) -> None
        if gpioHandle.GPIO in GPIOManager.__GPIOs:
            logger.info("Freeing GPIO " + str(gpioHandle.GPIO.Port))
            GPIOManager.__GPIOs[gpioHandle.GPIO] == False
