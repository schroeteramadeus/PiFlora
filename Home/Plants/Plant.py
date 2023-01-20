from Home.Hardware.Actors.Actor import Actor
from Home.Hardware.Sensors.Sensor import Sensor
import Home.Plants.PlantConfiguration as PC
import Home.Hardware.Sensors.Plant.PlantSensor as PS
import Home.Hardware.Actors.Water.Pump as P
from Home.Hardware.Sensors.Plant.PlantSensor import PlantSensorParameters as PSP

class Plant:

    PUMPHARDWAREID = "pump" #type: str

    def __init__(self, plantConfiguration, plantSensor, hardware = {}) -> None:
        #type: (PC.PlantConfiguration, PS.PlantSensor, dict[str, Actor | Sensor]) -> None

        self.__plantConfiguration = plantConfiguration #type: PC.PlantConfiguration
        self.__plantSensor = plantSensor #type: PS.PlantSensor
        self.__hardware = hardware #type: dict[str, Actor | Sensor]

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
        return self.__hardware[Plant.PUMPHARDWAREID]

    @Pump.setter
    def Pump(self, pump):
        #type: (P.Pump) -> None
        self.__hardware[Plant.PUMPHARDWAREID] = pump

    #TODO setter + getter for other standard hardware e.g. lamps?

    @staticmethod
    def FromPlant(plant, plantSensor, hardware):
        #type: (Plant, PS.PlantSensor, dict[str, Actor | Sensor]) -> Plant
        return Plant(plant.PlantConfiguration, plantSensor, hardware)

    def __str__(self):
        return self.PlantConfiguration.Name
