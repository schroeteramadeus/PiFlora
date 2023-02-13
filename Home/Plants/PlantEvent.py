from ..Utils.Event import Event

from typing import TYPE_CHECKING
if TYPE_CHECKING:  # Only imports the below statements during type checking
    from ..Plants.PlantManager import PlantManager
    from ..Plants.Plant import Plant
    import logging

class PlantEvent(Event):
    def __init__(self):
        super().__init__()
    #plants = all plants (on the same sensor), regardeless if having the error
    #errorList = dict with plants as keys that also have the same error, containing the time that the error was first detected
    #error = the actual error (code)
    def __call__(self, plantEventData):
        #type: (PlantEventData) -> None
        for eventhandler in self._eventhandlers:
            eventhandler(plantEventData)

class PlantEventData:
    def __init__(self, plantManager, plants, sensorData, error, errorPlants, logger) -> None:
        #type: (PlantManager, list[Plant], dict[str, object], str, dict[Plant, float], logging.Logger) -> None
        self.__plantManager = plantManager #type: PlantManager
        self.__plants = plants #type: list[Plant]
        self.__sensorData = sensorData #type: dict[str, object]
        self.__error = error #type: str
        self.__errorPlants = errorPlants #type: dict[Plant, float]
        self.__logger = logger #type: logging.Logger

    @property
    def PlantManager(self):
        #type: () -> PlantManager
        return self.__plantManager
    @property
    def Plants(self):
        #type: () -> list[Plant]
        return self.__plants
    @property
    def SensorData(self):
        #type: () -> dict[str, object]
        return self.__sensorData
    @property
    def Error(self):
        #type: () -> str
        return self.__error
    @property
    def ErrorPlants(self):
        #type: () -> dict[Plant, float]
        return self.__errorPlants
    @property
    def Logger(self):
        #type: () -> logging.Logger
        return self.__logger
    

class PlantChangedEvent(Event):

    def __init__(self):
        super().__init__()

    def __call__(self, plant, oldValue, newValue, valueType):
        #type: (Plant, object, object, str) -> None
        for eventhandler in self._eventhandlers:
            eventhandler(plant, oldValue, newValue, valueType)
