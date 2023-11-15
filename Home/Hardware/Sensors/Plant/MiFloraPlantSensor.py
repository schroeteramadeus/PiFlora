import logging

_importResolved = False

logger = logging.getLogger(__name__)

try:
    from miflora import miflora_poller # type: ignore
    from btlewrap import GatttoolBackend as BluetoothBackend# type: ignore
    from miflora.miflora_poller import (# type: ignore
        MI_BATTERY,
        MI_CONDUCTIVITY,
        MI_LIGHT,
        MI_MOISTURE,
        MI_TEMPERATURE,
    )
    _importResolved = True
except ImportError or ModuleNotFoundError:
    #print("Could not import Module: MiFlora, Running " + __file__ + " now in Debugmode")
    logger.warning("Could not import Module: MiFlora, Running " + __name__ + " now in Debugmode")

import time
from ...BluetoothManager import BluetoothManager
from .PlantSensor import PlantSensor, PlantSensorParameters

debugMode = not _importResolved

def IsDebugMode():
    global debugMode
    return debugMode
def SetDebugMode(value : bool):
    global debugMode
    debugMode = value


#TODO add debug mode
class MiFloraPlantSensor(PlantSensor):
    
    __usedSensors : list[str] = []

    def __init__(self, mac : str) -> None:
        global debugMode
        super().__init__()
        self._id : str = mac
        self.__isDebugMode : bool = False
        self.__firmware : str = ""
        self.__name : str = ""

        if not self._id in MiFloraPlantSensor.__usedSensors:
            logger.info("Binding plant sensor " + self._id)
            self.__usedSensors.append(self._id)
            self.UpdateDebugMode(debugMode)
        else:
            raise ConnectionAbortedError("Not a valid sensor or already used")
    
    def __del__(self):
        logger.info("Freeing plant sensor " + self._id)
        self.__usedSensors.remove(self._id)

    def UpdateDebugMode(self, debugMode : bool) -> None:
        if not debugMode:
            self.__poller = miflora_poller.MiFloraPoller(self._id, BluetoothBackend)
            self.__firmware = self.__poller.firmware_version()
            self.__name = self.__poller.name()
        else:
            self.__isDebugMode = True
            self.__name = "DEBUG"

    @property
    def IsDebug(self):
        return self.__isDebugMode

    @property
    def Firmware(self):
        return self.__firmware
    
    @property
    def Name(self):
        return self.__name

    @property
    def Mac(self):
        return self._id

    def PollSensor(self):
        return self.PollSensor(1)

    def PollSensor(self, pollCount : int = 5) -> dict[str,object]:
        output = {}
        currentTime = time.time()
        if not self.IsDebug:
            output = {
                PlantSensorParameters.BATTERY: self.__poller.parameter_value(MI_BATTERY),
                PlantSensorParameters.TEMPERATURE: 0.0,
                PlantSensorParameters.MOISTURE: 0.0,
                PlantSensorParameters.LIGHT: 0.0,
                PlantSensorParameters.CONDUCTIVITY: 0.0,
            }
            for x in range(pollCount):
                data = {
                    PlantSensorParameters.TEMPERATURE: float(self.__poller.parameter_value(MI_TEMPERATURE) / pollCount),
                    PlantSensorParameters.MOISTURE: float(self.__poller.parameter_value(MI_MOISTURE) / pollCount),
                    PlantSensorParameters.LIGHT: float(self.__poller.parameter_value(MI_LIGHT) / pollCount),
                    PlantSensorParameters.CONDUCTIVITY: float(self.__poller.parameter_value(MI_CONDUCTIVITY) / pollCount),
                }
                output[PlantSensorParameters.TEMPERATURE] += data[PlantSensorParameters.TEMPERATURE]
                output[PlantSensorParameters.MOISTURE] += data[PlantSensorParameters.MOISTURE]
                output[PlantSensorParameters.LIGHT] += data[PlantSensorParameters.LIGHT]
                output[PlantSensorParameters.CONDUCTIVITY] += data[PlantSensorParameters.CONDUCTIVITY]
                self.__poller.clear_cache()
                self.__poller.clear_history()
                if x < pollCount - 1:
                    time.sleep(10)
        else:
            output = {
                PlantSensorParameters.BATTERY: 100,
                PlantSensorParameters.TEMPERATURE: 22,
                PlantSensorParameters.MOISTURE: 50,
                PlantSensorParameters.LIGHT: 50,
                PlantSensorParameters.CONDUCTIVITY: 50,
            }
        timeNeeded =  time.time() - currentTime
        return output

    def __str__(self):
        return self.Mac