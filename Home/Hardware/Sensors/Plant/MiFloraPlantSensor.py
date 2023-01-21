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
    print("Could not import Module: MiFlora, Running " + __file__ + " now in Debugmode")
    logger.warning("Could not import Module: MiFlora, Running " + __file__ + " now in Debugmode")

import time
import Home.Hardware.BluetoothManager as BM
import Home.Hardware.Sensors.Plant.PlantSensor as P

debugMode = not _importResolved

#TODO add debug mode
class MiFloraPlantSensor(P.PlantSensor):
    
    __usedSensors = [] #type: list[str]

    def __init__(self, mac) -> None:
        #type: (str) -> None
        super().__init__()
        self._id = mac #type: str
        self.__isDebugMode = False
        self.__firmware = "" #type: str
        self.__name = "" #type: str

        if not self._id in MiFloraPlantSensor.__usedSensors:
            logger.info("Binding plant sensor " + self._id)
            self.__usedSensors.append(self._id)
            self.UpdateDebugMode(debugMode)
        else:
            raise ConnectionAbortedError("Not a valid sensor or already used")
    
    def __del__(self):
        logger.info("Freeing plant sensor " + self._id)
        self.__usedSensors.remove(self._id)

    def UpdateDebugMode(self, debugMode):
        #type: (bool) -> None
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

    def PollSensor(self, pollCount = 5):
        #type: (int) -> dict[str,object]
        output = {}
        currentTime = time.time()
        if not self.IsDebug:
            output = {
                P.PlantSensorParameters.BATTERY: self.__poller.parameter_value(MI_BATTERY),
                P.PlantSensorParameters.TEMPERATURE: 0.0,
                P.PlantSensorParameters.MOISTURE: 0.0,
                P.PlantSensorParameters.LIGHT: 0.0,
                P.PlantSensorParameters.CONDUCTIVITY: 0.0,
            }
            for x in range(pollCount):
                data = {
                    P.PlantSensorParameters.TEMPERATURE: float(self.__poller.parameter_value(MI_TEMPERATURE) / pollCount),
                    P.PlantSensorParameters.MOISTURE: float(self.__poller.parameter_value(MI_MOISTURE) / pollCount),
                    P.PlantSensorParameters.LIGHT: float(self.__poller.parameter_value(MI_LIGHT) / pollCount),
                    P.PlantSensorParameters.CONDUCTIVITY: float(self.__poller.parameter_value(MI_CONDUCTIVITY) / pollCount),
                }
                output[P.PlantSensorParameters.TEMPERATURE] += data[P.PlantSensorParameters.TEMPERATURE]
                output[P.PlantSensorParameters.MOISTURE] += data[P.PlantSensorParameters.MOISTURE]
                output[P.PlantSensorParameters.LIGHT] += data[P.PlantSensorParameters.LIGHT]
                output[P.PlantSensorParameters.CONDUCTIVITY] += data[P.PlantSensorParameters.CONDUCTIVITY]
                self.__poller.clear_cache()
                self.__poller.clear_history()
                if x < pollCount - 1:
                    time.sleep(10)
        else:
            output = {
                P.PlantSensorParameters.BATTERY: 100,
                P.PlantSensorParameters.TEMPERATURE: 22,
                P.PlantSensorParameters.MOISTURE: 50,
                P.PlantSensorParameters.LIGHT: 50,
                P.PlantSensorParameters.CONDUCTIVITY: 50,
            }
        timeNeeded =  time.time() - currentTime
        return output

    def __str__(self):
        return self.Mac