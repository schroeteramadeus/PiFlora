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
    def __call__(self, plantManager, plants, sensorData, error, errorPlants, logger):
        #type: (PM.PlantManager, list[P.Plant], dict[str, object], str, dict[P.Plant, float], logging.Logger) -> None
        for eventhandler in self.__eventhandlers:
            eventhandler(plantManager, plants, sensorData, error, errorPlants, logger)