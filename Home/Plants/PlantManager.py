import json
from Home.Hardware.Actors.Water.Pump import Pump
import Home.Plants.Plant as P
from Home.Hardware.Sensors.Plant.PlantSensor import PlantSensorParameters as PSP
import time
import logging
import Home.Plants.PlantEvent as PE
import Home.Hardware.Sensors.Water.WaterSensor as WS
import threading
from Home.Utils.WakeableSleep import WakeableSleep
import Home.Hardware.Sensors.Plant.PlantSensor as PS

logger = logging.getLogger(__name__)

debugMode = False

class PlantManager:

    __staticId = 0
    __batterLowLevel = 5
    __consecutivePolls = 1 #try to use criticalInterval instead (so no DoS happens)
    __maximumSleepingTime = 5 #for threads waking up to check if manager is still running

    def __init__(self, waterSensor, plants = []) -> None:
        #type: (WS.WaterSensor, list[P.Plants]) -> None
        self.__id = PlantManager.__staticId + 1
        PlantManager.__staticId = PlantManager.__staticId + 1
        self.__logger = logger.getChild("PlantManager" + str(self.__id))
        self.__logger.info("Initializing plant manager...")
        #type: (list[P.Plant]) -> None
        self.__sensorsLock = threading.Lock()
        self.__sensors = {} #type: dict[PS.PlantSensor, list[P.Plant]] #plants sorted after sensors
        self.__errorsLock = threading.Lock()
        self.__errors = {} #type: dict[P.Plant, dict[str, float]] #errors for each plant
        self.__criticalInterval = 900 #type: float #15 min #time that needs to pass in order for an error to be regarded as critical (action needed)
        self.__pollInterval = 300 #type: float #5min
        self.__sensorDataCacheLock = threading.Lock()
        self.__sensorDataCache = {} #type: dict[str, dict[str, object]]
        self.__lastPollUpdate = -1 #type: float
        self.__lastActionUpdate = -1 #type: float

        self.__onWaterError = PE.PlantEvent()
        #self.__onWaterError += PlantManager.ErrorFixByWateringPlant

        self.__onBatteryError = PE.PlantEvent()
        #self.__onBatteryError += PlantManager.ErrorFixByEmail

        self.__onConductivityError = PE.PlantEvent()
        #self.__onConductivityError += PlantManager.ErrorFixByEmail

        self.__onTemperatureError = PE.PlantEvent()
        #self.__onTemperatureError += PlantManager.ErrorFixByEmail

        self.__onLightError = PE.PlantEvent()
        #self.__onLightError += PlantManager.ErrorFixByEmail

        self.__waterSensor = waterSensor #type: WS.WaterSensor
        self.__isRunning = False #type: bool
        self.__actionThread = None #type: threading.Thread
        self.__pollThread = None #type: threading.Thread
        self.__cancellationToken = None #type: threading.Event
        self.__startedInDebugMode = False #type: bool

        for plant in plants:
            self.Add(plant)
        self.__logger.debug("Plant manager successfully initialized")

    @property
    def OnWaterError(self):
        #type: () -> PE.PlantEvent
        return self.__onWaterError

    @property
    def OnBatteryError(self):
        #type: () -> PE.PlantEvent
        return self.__onBatteryError

    @property
    def OnConductivityError(self):
        #type: () -> PE.PlantEvent
        return self.__onConductivityError

    @property
    def OnTemperatureError(self):
        #type: () -> PE.PlantEvent
        return self.__onTemperatureError

    @property
    def OnLightError(self):
        #type: () -> PE.PlantEvent
        return self.__onLightError

    @property
    def Logger(self):
        #type: () -> logging.Logger
        return self.__logger

    @property
    def WaterSensor(self):
        #type: () -> WS.WaterSensor
        return self.__waterSensor

    @property
    def IsRunning(self):
        #type: () -> bool
        return self.__isRunning

    @property
    def IsDebug(self):
        #type: () -> bool
        return (debugMode and not self.IsRunning) or self.__startedInDebugMode
    
    @property
    def Plants(self):
        #type: () -> list[P.Plant]
        plants = []
        with self.__sensorsLock:
            for sensor in self.__sensors:
                sensorPlants = self.__sensors[sensor]
                for plant in sensorPlants:
                    plants.append(plant)
        return plants

    @property
    def Sensors(self):
        #type: () -> list[PS.PlantSensor]
        sensors = []
        with self.__sensorsLock:
            sensors = list(self.__sensors)
        return sensors
        
    @property
    def Pumps(self):
        #type: () -> list[Pump]
        pumps = []
        plants = self.Plants

        for plant in plants:
            if not plant.Pump in pumps:
                pumps.append(plant.Pump)

        return pumps

    def Add(self, plant):
        #type: (P.Plant) -> None
        #TODO check if plant with same id exists then throw error
        self.__logger.debug("Adding plant " + plant.PlantConfiguration.Name + " to plant manager...")
        added = False
        with self.__sensorsLock:
            for sensor in self.__sensors:
                if sensor == plant.PlantSensor:
                    self.__sensors[sensor].append(plant)
                    added = True
            if not added:
                newSensor = [plant]
                self.__sensors[plant.PlantSensor] = newSensor

        with self.__errorsLock:
            self.__errors[plant] = {}

        self.__logger.info("Successfully added plant " + plant.PlantConfiguration.Name + " to plant manager")

    def Remove(self, plant):
        self.__logger.debug("Removing plant " + plant.PlantConfiguration.Name + " from plant manager")
        #type: (P.Plant) -> None
        with self.__sensorsLock:
            for sensor in self.__sensors:
                if sensor == plant.PlantSensor:
                    if len(self.__sensors[sensor]) > 1:
                        self.__sensors[sensor].remove(plant)
                    else:
                        self.__sensors.pop(sensor)
                    break
        with self.__errorsLock:
            self.__errors[plant] = None
        self.__logger.info("Successfully removed plant " + plant.PlantConfiguration.Name + " from plant manager")

    def Start(self):
        if not self.IsRunning:
            self.__logger.debug("Starting...")
            if not debugMode:
                self.__cancellationToken = threading.Event()
                self.__pollThread = threading.Thread(target=self.UpdatePoll)
                self.__actionThread = threading.Thread(target=self.UpdateAction)

                self.__pollThread.start()
                self.__actionThread.start()
                self.__startedInDebugMode = False
            else:
                self.__startedInDebugMode = True

            self.__isRunning = True
            self.__logger.info("Started")

    def Stop(self):
        if self.IsRunning:
            self.__logger.debug("Stopping...")
            if not self.__startedInDebugMode:
                self.__cancellationToken.set()
                self.__pollThread.join()
                self.__actionThread.join()

                self.__cancellationToken = None
                self.__pollThread = None
                self.__actionThread = None

            self.__startedInDebugMode = False
            self.__isRunning = False
            self.__logger.info("Stopped")

    def UpdatePoll(self):
        while not self.__cancellationToken.is_set():
            self.__logger.info("Plant manager starts new polling round...")
            t = time.time()
            sensors = {}
            with self.__sensorsLock:
                sensors = self.__sensors
            for sensor in sensors:
                #poll data and log it
                plants = sensors[sensor]
                self.__logger.debug("Plant manager polling sensor [" + str(sensor) + "]...")
                data = {}
                with self.__sensorDataCacheLock:
                    self.__sensorDataCache[sensor] = plants[0].PlantSensor.PollSensor(self.__consecutivePolls)
                    data = self.__sensorDataCache[sensor]
                self.__logger.debug("Plant manager successfully polled sensor [" + str(sensor) + "]")
                if self.__cancellationToken.is_set():
                    break
                #date = time.localtime(t)
                #dateString = str(date.tm_mday) + "." + str(date.tm_mon) + "." + str(date.tm_year) + " " + str(date.tm_hour) + ":" + str(date.tm_min) + ":" + str(date.tm_sec) + " " + str(date.tm_zone)
                errorDict = {} #type: dict[str,float]
                plantString = ""
                dataString = ""
                errorString = ""

                for x in data:
                    dataString = x + ": " + str(data[x]) + ", "
                for x in range(len(plants)):
                    plantString = plants[x].PlantConfiguration.Name + ", "
                    if data[PSP.BATTERY] <= self.__batterLowLevel:
                        errorString += "Battery: Low (" + data[PSP.BATTERY] + "%), "
                        errorDict[PSP.BATTERY] = t
                    if not plants[x].PlantConfiguration.TemperatureSpan.BetweenInclude(data[PSP.TEMPERATURE]):
                        errorString += "Temperature: insufficient (" + str(data[PSP.TEMPERATURE]) + "°C), "
                        errorDict[PSP.TEMPERATURE] = t
                    if not plants[x].PlantConfiguration.MoistureSpan.BetweenInclude(data[PSP.MOISTURE]):
                        errorString += "Moisture: insufficient (" + str(data[PSP.MOISTURE]) + "), "
                        errorDict[PSP.MOISTURE] = t
                    if not plants[x].PlantConfiguration.LightSpan.BetweenInclude(data[PSP.LIGHT]):
                        errorString += "Light level: insufficient (" + str(data[PSP.LIGHT]) + "), "
                        errorDict[PSP.LIGHT] = t
                    if not plants[x].PlantConfiguration.ConductivitySpan.BetweenInclude(data[PSP.CONDUCTIVITY]):
                        errorString += "Fertilizer: insufficient (" + str(data[PSP.CONDUCTIVITY]) + ")"
                        errorDict[PSP.CONDUCTIVITY] = t
                    
                    #check if errors still persist (else delete)
                    with self.__errorsLock:
                        for oldErrorKey in self.__errors[plants[x]]:
                            entryValid = False
                            for newErrorKey in errorDict:
                                if self.__errors[plants[x]][oldErrorKey] == None:
                                    self.__errors[plants[x]][oldErrorKey] = errorDict[newErrorKey]
                                entryValid = True
                            if not entryValid:
                                self.__errors[plants[x]][oldErrorKey] = None
            
                self.__logger.info("Plant manager successfully updated polling data for plants [" + str(sensor) + "]: " + plantString)
                self.__logger.debug("Plant manager acquired new polling data for plants [" + str(sensor) + "]: " + dataString)
                if len(errorDict) > 0:
                    self.__logger.debug("Plant manager detected errors [" + str(sensor) + "]: " + errorString)
                
                if self.__cancellationToken.is_set():
                    break

            if self.__cancellationToken.is_set():
                self.__logger.info("Plant manager shutting down polling thread...")
            
            self.__lastPollUpdate = time.time()

            timeNeeded = self.__lastPollUpdate - t
            nextPollIn = self.__pollInterval - timeNeeded
            if nextPollIn <= 0:
                self.__logger.info("Poll time for plant manager: "   + str(timeNeeded / 60) + "min")
                self.__logger.debug("Plant manager finished poll with " + str(abs(nextPollIn)) + "s delay")
            else:
                self.__logger.info("Poll time for plant manager: " + str(timeNeeded / 60) + "min, sleeping now for next poll in: " + str(nextPollIn / 60) + "min")
                WakeableSleep(self.__cancellationToken, nextPollIn, PlantManager.__maximumSleepingTime)


        if self.__cancellationToken.is_set():
            self.__logger.debug("Poll thread finished")
        else:
            self.__logger.warning("Poll thread closed unexpectedly")
    
    def UpdateAction(self):
        while not self.__cancellationToken.is_set():
            self.__logger.info("Plant manager starts new fixing round...")
            t = time.time()
            #date = time.localtime(t)
            #dateString = str(date.tm_mday) + "." + str(date.tm_mon) + "." + str(date.tm_year) + " " + str(date.tm_hour) + ":" + str(date.tm_min) + ":" + str(date.tm_sec) + " " + str(date.tm_zone)
            currentErrors = {}
            currentSensors = {}
            with self.__errorsLock:
                currentErrors = self.__errors
            with self.__sensorsLock:
                currentSensors = self.__sensors
            
            for sensor in currentSensors:
                plants = currentSensors[sensor]
                errors = {} #type: dict[str, dict[P.Plant, float]]
                sensorData = {} #type: dict[str, object]
                with self.__sensorDataCacheLock:
                    sensorData = self.__sensorDataCache[sensor]

                #foreach plant from the same sensor
                for plant in plants:
                    for error in currentErrors[plant]:
                        errorTime = currentErrors[plant][error]
                        if errorTime + self.__criticalInterval >= t:
                            errors[error][plant] = errorTime
                        else:
                            #no action needed
                            pass
                if self.__cancellationToken.is_set():
                    break

                for error in errors:
                    errorPlants = errors[error]
                    if error == PSP.BATTERY:
                        self.__logger.debug("Plant manager fixing low battery...")
                        if len(self.__onBatteryError) > 0:
                            self.__onBatteryError(self, plants, sensorData, error, errorPlants, self.__logger)
                        else:
                            self.__logger.critical("Plant manager can not fix battery")
                    elif error == PSP.CONDUCTIVITY:
                        self.__logger.debug("Plant manager fixing conductivity...")
                        if len(self.__onConductivityError) > 0:
                            self.__onConductivityError(self, plants, sensorData, error, errorPlants, self.__logger)
                        else:
                            self.__logger.critical("Plant manager can not fix conductivity")
                    elif error == PSP.LIGHT:
                        self.__logger.debug("Plant manager fixing light...")
                        if len(self.__onLightError) > 0:
                            self.__onLightError(self, plants, sensorData, error, errorPlants, self.__logger)
                        else:
                            self.__logger.critical("Plant manager can not fix light")
                    elif error == PSP.MOISTURE:
                        self.__logger.debug("Plant manager fixing moisture...")
                        if len(self.__onWaterError) > 0:
                            self.__onWaterError(self, plants, sensorData, error, errorPlants, self.__logger)
                        else:
                            self.__logger.critical("Plant manager can not fix moisture")
                    elif error == PSP.TEMPERATURE:
                        self.__logger.debug("Plant manager fixing temperature...")
                        if len(self.__onTemperatureError) > 0:
                            self.__onTemperatureError(self, plants, sensorData, error, errorPlants, self.__logger)
                        else:
                            self.__logger.critical("Plant manager can not fix temperature")

                    if self.__cancellationToken.is_set():
                        break

                if self.__cancellationToken.is_set():
                    break

            if self.__cancellationToken.is_set():
                self.__logger.info("Plant manager shutting down action thread...")

            self.__lastActionUpdate = time.time()
            timeNeeded = self.__lastActionUpdate - t
            nextFixIn = self.__criticalInterval - timeNeeded
            if nextFixIn <= 0:
                self.__logger.info("Plant manager finished fixing round in " + str(timeNeeded / 60) + "min")
                self.__logger.debug("Plant manager finished fixing round with " + str(abs(nextFixIn)) + "s delay")
            else:
                self.__logger.info("Plant manager finished fixing round in " + str(timeNeeded / 60) + "min, sleeping now for next fixing round in: " + str(nextFixIn / 60) + "min")
                WakeableSleep(self.__cancellationToken, nextFixIn, PlantManager.__maximumSleepingTime)

        if self.__cancellationToken.is_set():
            self.__logger.debug("Action thread finished")
        else:
            self.__logger.warning("Action thread closed unexpectedly")

    def ErrorFixByEmail(plantManager, plant, sensorData, error, errorPlants, logger):
        #type: (PlantManager, list[P.Plant], dict[str, object], str, dict[P.Plant, float], logging.Logger) -> None
        #TODO
        pass

    def ErrorFixByWateringPlant(plantManager, plant, sensorData, error, errorPlants, logger):
        #type: (PlantManager, list[P.Plant], dict[str, object], str, dict[P.Plant, float], logging.Logger) -> None
        if error == PSP.MOISTURE:
            if plant.Pump != None:
                #TODO merge all different pumps
                #TODO find minimal maximum of water needed by all errorPlants
                #TODO FAILSAFE: if last time watered > lastPollUpdate + updateInterval #error REALLY persists
                if plantManager.WaterSensor.PollSensor()[WS.WATER_SENSOR_UNDER_WATER]:
                    waterNeeded = plant.PlantConfiguration.MoistureSpan.Max - sensorData[PSP.MOISTURE]
                    logger.debug("Watering " + plant.PlantConfiguration.Name + " with " + str(waterNeeded) + "ml")
                    waterGiven = plant.Pump.Water(waterNeeded)
                    logger.info("Successfully watered " + plant.PlantConfiguration.Name + " with " + str(waterGiven) + "ml")
                    logger.debug("Water difference of " + plant.PlantConfiguration.Name + " is " + str(waterGiven - waterNeeded) + "ml")
                else:
                    logger.critical("Could not water " + plant.PlantConfiguration.Name + ", because there is not enough water left")
            else:
                logger.critical("Could not water " + plant.PlantConfiguration.Name + ", because there is no pump configured")
        else:
            logger.warning("FAILSAFE: Not watering " + plant.PlantConfiguration.Name + ", because error type was " + error + " instead of " + PSP.MOISTURE)