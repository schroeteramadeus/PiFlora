from typing import Callable
from Home.Hardware.Actors.Actor import Actor
from Home.Hardware.Sensors.Sensor import Sensor
import Home.Plants.PlantConfiguration as PC
import Home.Hardware.Sensors.Plant.PlantSensor as PS
import Home.Hardware.Actors.Water.Pump as P
from Home.Hardware.Sensors.Plant.PlantSensor import PlantSensorParameters as PSP
from Home.Plants.PlantEvent import PlantChangedEvent

class Plant:

    HARDWARE_PUMP = "pump" #type: str
    HARDWARE_PLANTSENSOR = "plantSensor" #type: str

    EVENTTYPE_HARDWARE = "hardware"
    EVENTTYPE_PLANTSENSOR = "plantSensor"
    EVENTTYPE_PUMP = "pump"
    EVENTTYPE_PLANTCONFIGURATION = "configuration"

    def __init__(self, plantConfiguration, hardware = {}) -> None:
        #type: (PC.PlantConfiguration, dict[str, Actor | Sensor]) -> None
        self.__onPlantChanged = PlantChangedEvent() #type: PlantChangedEvent
        self.__plantConfiguration = plantConfiguration #type: PC.PlantConfiguration
        self.__hardware = hardware #type: dict[str, Actor | Sensor]

    def AddOnPlantChangedEventHandler(self, handler):
        #type: (Callable([P.Plant, object, object, str], None)) -> None
        self.__onPlantChanged += handler
        
    def RemoveOnPlantChangedEventHandler(self, handler):
        #type: (Callable([P.Plant, object, object, str], None)) -> None
        self.__onPlantChanged -= handler

    @property
    def PlantSensor(self):
        #type: () -> PS.PlantSensor
        return self.__hardware[Plant.HARDWARE_PLANTSENSOR]

    @PlantSensor.setter
    def PlantSensor(self, plantSensor):
        #type: (PS.PlantSensor) -> None
        old = self.__hardware[Plant.HARDWARE_PLANTSENSOR]
        self.__hardware[Plant.HARDWARE_PLANTSENSOR] = plantSensor
        self.__onPlantChanged(self, old, plantSensor, Plant.EVENTTYPE_PLANTSENSOR)

    @property
    def PlantConfiguration(self):
        #type: () -> PC.PlantConfiguration
        return self.__plantConfiguration
    
    @PlantConfiguration.setter
    def PlantConfiguration(self, plantConfiguration):
        #type: (PC.PlantConfiguration) -> None
        old = self.__plantConfiguration
        self.__plantConfiguration = plantConfiguration
        self.__onPlantChanged(self, old, plantConfiguration, Plant.EVENTTYPE_PLANTCONFIGURATION)

    @property
    def Pump(self):
        #type: () -> P.Pump
        return self.__hardware[Plant.HARDWARE_PUMP]

    @Pump.setter
    def Pump(self, pump):
        #type: (P.Pump) -> None
        old = self.__hardware[Plant.HARDWARE_PUMP]
        self.__hardware[Plant.HARDWARE_PUMP] = pump
        self.__onPlantChanged(self, old, pump, Plant.EVENTTYPE_PUMP)

    #TODO setter + getter for other standard hardware e.g. lamps?

    @property
    def Hardware(self):
        #type: () -> dict[str, Actor | Sensor]
        return self.__hardware

    @staticmethod
    def FromPlant(plant, newHardware):
        #type: (Plant, dict[str, Actor | Sensor]) -> Plant
        return Plant(plant.PlantConfiguration, newHardware)

    def __str__(self):
        return self.PlantConfiguration.Name
