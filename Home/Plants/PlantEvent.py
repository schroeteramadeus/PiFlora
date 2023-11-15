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
    def __call__(self, plantEventData : 'PlantEventData') -> None:
        for eventhandler in self._eventhandlers:
            eventhandler(plantEventData)

class PlantEventData:
    def __init__(self, plantManager : PlantManager, plants : list[Plant], sensorData : dict[str, object], error : str, errorPlants : dict[Plant, float], logger : logging.Logger) -> None:
        self.__plantManager : PlantManager= plantManager
        self.__plants : list[Plant] = plants
        self.__sensorData : dict[str, object] = sensorData
        self.__error : str = error
        self.__errorPlants : dict[Plant, float] = errorPlants
        self.__logger : logging.Logger = logger

    @property
    def PlantManager(self) -> PlantManager:
        return self.__plantManager
    @property
    def Plants(self) -> list[Plant]:
        return self.__plants
    @property
    def SensorData(self) -> dict[str, object]:
        return self.__sensorData
    @property
    def Error(self) -> str:
        return self.__error
    @property
    def ErrorPlants(self) -> dict[Plant, float]:
        return self.__errorPlants
    @property
    def Logger(self) -> logging.Logger:
        return self.__logger
    

class PlantChangedEvent(Event):

    def __init__(self):
        super().__init__()

    def __call__(self, plant : Plant, oldValue : object, newValue : object, valueType : str):
        for eventhandler in self._eventhandlers:
            eventhandler(plant, oldValue, newValue, valueType)
