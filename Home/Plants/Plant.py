from typing import Callable
from ..Hardware.Actors.Actor import Actor
from ..Hardware.Sensors.Sensor import Sensor
from .PlantConfiguration import PlantConfiguration
from ..Hardware.Sensors.Plant.PlantSensor import PlantSensor
from ..Hardware.Actors.Water.Pump import Pump
from .PlantEvent import PlantChangedEvent

class Plant:

    HARDWARE_PUMP = "pump" #type: str
    HARDWARE_PLANTSENSOR = "plantSensor" #type: str

    EVENTTYPE_HARDWARE = "hardware"
    EVENTTYPE_PLANTSENSOR = "plantSensor"
    EVENTTYPE_PUMP = "pump"
    EVENTTYPE_PLANTCONFIGURATION = "configuration"

    def __init__(self, plantConfiguration, hardware = {}) -> None:
        #type: (PlantConfiguration, dict[str, Actor | Sensor]) -> None
        self.__onPlantChanged = PlantChangedEvent() #type: PlantChangedEvent
        self.__plantConfiguration = plantConfiguration #type: PlantConfiguration
        self.__hardware = hardware #type: dict[str, Actor | Sensor]

    def AddOnPlantChangedEventHandler(self, handler):
        #type: (Callable([Plant, object, object, str], None)) -> None
        self.__onPlantChanged += handler
        
    def RemoveOnPlantChangedEventHandler(self, handler):
        #type: (Callable([Plant, object, object, str], None)) -> None
        self.__onPlantChanged -= handler

    @property
    def PlantSensor(self):
        #type: () -> PlantSensor
        return self.__hardware[Plant.HARDWARE_PLANTSENSOR]

    @PlantSensor.setter
    def PlantSensor(self, plantSensor):
        #type: (PlantSensor) -> None
        old = self.__hardware[Plant.HARDWARE_PLANTSENSOR]
        self.__hardware[Plant.HARDWARE_PLANTSENSOR] = plantSensor
        self.__onPlantChanged(self, old, plantSensor, Plant.EVENTTYPE_PLANTSENSOR)

    @property
    def PlantConfiguration(self):
        #type: () -> PlantConfiguration
        return self.__plantConfiguration
    
    @PlantConfiguration.setter
    def PlantConfiguration(self, plantConfiguration):
        #type: (PlantConfiguration) -> None
        old = self.__plantConfiguration
        self.__plantConfiguration = plantConfiguration
        self.__onPlantChanged(self, old, plantConfiguration, Plant.EVENTTYPE_PLANTCONFIGURATION)

    @property
    def Pump(self):
        #type: () -> Pump
        return self.__hardware[Plant.HARDWARE_PUMP]

    @Pump.setter
    def Pump(self, pump):
        #type: (Pump) -> None
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
