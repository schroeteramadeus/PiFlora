import Home.Utils.Event as E

from typing import TYPE_CHECKING
if TYPE_CHECKING:  # Only imports the below statements during type checking
    import Home.Plants.PlantManager as PM
    import Home.Plants.Plant as P
    import logging

class PlantEvent(E.Event):
    #plants = all plants (on the same sensor), regardeless if having the error
    #errorList = dict with plants as keys that also have the same error, containing the time that the error was first detected
    #error = the actual error (code)
    def __call__(self, plantEventData):
        #type: (PlantEventData) -> None
        for eventhandler in self.__eventhandlers:
            eventhandler(plantEventData)

class PlantEventData:
    def __init__(self, plantManager, plants, sensorData, error, errorPlants, logger) -> None:
        #type: (PM.PlantManager, list[P.Plant], dict[str, object], str, dict[P.Plant, float], logging.Logger) -> None
        self.__plantManager = plantManager #type: PM.PlantManager
        self.__plants = plants #type: list[P.Plant]
        self.__sensorData = sensorData #type: dict[str, object]
        self.__error = error #type: str
        self.__errorPlants = errorPlants #type: dict[P.Plant, float]
        self.__logger = logger #type: logging.Logger

    @property
    def PlantManager(self):
        #type: () -> PM.PlantManager
        return self.__plantManager
    @property
    def Plants(self):
        #type: () -> list[P.Plant]
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
        #type: () -> dict[P.Plant, float]
        return self.__errorPlants
    @property
    def Logger(self):
        #type: () -> logging.Logger
        return self.__logger