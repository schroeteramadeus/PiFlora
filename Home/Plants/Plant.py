from __future__ import annotations
from typing import Callable
from ..Hardware.Actors.Actor import Actor
from ..Hardware.Sensors.Sensor import Sensor
from .PlantConfiguration import PlantConfiguration as plant_configuration
from ..Hardware.Sensors.Plant.PlantSensor import PlantSensor as plant_sensor
from ..Hardware.Actors.Water.Pump import Pump
from .PlantEvent import PlantChangedEvent

class Plant:

    HARDWARE_PUMP = "pump" #type: str
    HARDWARE_PLANTSENSOR = "plantSensor" #type: str

    EVENTTYPE_HARDWARE = "hardware"
    EVENTTYPE_PLANTSENSOR = "plantSensor"
    EVENTTYPE_PUMP = "pump"
    EVENTTYPE_PLANTCONFIGURATION = "configuration"

    def __init__(self, plantConfiguration : plant_configuration, hardware : dict[str, Actor | Sensor] = {}) -> None:
        self.__onPlantChanged : PlantChangedEvent = PlantChangedEvent()
        self.__plantConfiguration : plant_configuration = plantConfiguration
        self.__hardware : dict[str, Actor | Sensor] = hardware

    def AddOnPlantChangedEventHandler(self, handler : Callable([Plant, object, object, str], None)) -> None:
        self.__onPlantChanged += handler
        
    def RemoveOnPlantChangedEventHandler(self, handler : Callable([Plant, object, object, str], None)) -> None:
        self.__onPlantChanged -= handler

    @property
    def PlantSensor(self) -> plant_sensor:
        return self.__hardware[Plant.HARDWARE_PLANTSENSOR]

    @PlantSensor.setter
    def PlantSensor(self, plantSensor : plant_sensor) -> None:
        old = self.__hardware[Plant.HARDWARE_PLANTSENSOR]
        self.__hardware[Plant.HARDWARE_PLANTSENSOR] = plantSensor
        self.__onPlantChanged(self, old, plantSensor, Plant.EVENTTYPE_PLANTSENSOR)

    @property
    def PlantConfiguration(self) -> plant_configuration:
        return self.__plantConfiguration
    
    @PlantConfiguration.setter
    def PlantConfiguration(self, plantConfiguration : plant_configuration) -> None:
        old = self.__plantConfiguration
        self.__plantConfiguration = plantConfiguration
        self.__onPlantChanged(self, old, plantConfiguration, Plant.EVENTTYPE_PLANTCONFIGURATION)

    @property
    def Pump(self) -> Pump:
        return self.__hardware[Plant.HARDWARE_PUMP]

    @Pump.setter
    def Pump(self, pump : Pump) -> None:
        old = self.__hardware[Plant.HARDWARE_PUMP]
        self.__hardware[Plant.HARDWARE_PUMP] = pump
        self.__onPlantChanged(self, old, pump, Plant.EVENTTYPE_PUMP)

    #TODO setter + getter for other standard hardware e.g. lamps?

    @property
    def Hardware(self) -> dict[str, Actor | Sensor]:
        return self.__hardware

    @staticmethod
    def FromPlant(plant : Plant, newHardware : dict[str, Actor | Sensor]) -> Plant:
        return Plant(plant.PlantConfiguration, newHardware)

    def __str__(self) -> str:
        return self.PlantConfiguration.Name
