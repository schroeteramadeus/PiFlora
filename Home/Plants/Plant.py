import Home.Plants.PlantConfiguration as PC
import Home.Hardware.Sensors.Plant.PlantSensor as PS
import Home.Hardware.Actors.Water.Pump as P
from Home.Hardware.Sensors.Plant.PlantSensor import PlantSensorParameters as PSP

class Plant:
    def __init__(self, plantConfiguration, plantSensor, pump) -> None:
        #type: (PC.PlantConfiguration, PS.PlantSensor, P.Pump) -> None

        self.__plantConfiguration = plantConfiguration #type: PC.PlantConfiguration
        self.__plantSensor = plantSensor #type: PS.PlantSensor
        self.__pump = pump #type: P.Pump
        self.__lastData = dict #type: dict[str, object]

    @property
    def PlantSensor(self):
        #type: () -> PS.PlantSensor
        return self.__plantSensor

    @PlantSensor.setter
    def PlantSensor(self, plantSensor):
        #type: (PS.PlantSensor) -> None
        self.__plantSensor = plantSensor

    @property
    def PlantConfiguration(self):
        #type: () -> PC.PlantConfiguration
        return self.__plantConfiguration
    
    @PlantConfiguration.setter
    def PlantConfiguration(self, plantConfiguration):
        #type: (PC.PlantConfiguration) -> None
        self.__plantConfiguration = plantConfiguration

    @property
    def Pump(self):
        #type: () -> P.Pump
        return self.__pump

    @Pump.setter
    def Pump(self, pump):
        #type: (P.Pump) -> None
        self.__pump = pump

    @staticmethod
    def FromPlant(plant, plantSensor, pump):
        #type: (Plant, PS.PlantSensor, P.Pump) -> Plant
        return Plant(plant.PlantConfiguration, plantSensor, pump)

    def __str__(self):
        return self.PlantConfiguration.Name
