from ..Hardware.Actors.Water.Pump import Pump
from .Plant import Plant
from ..Hardware.Sensors.Plant.PlantSensor import PlantSensorParameters as PSP
import time
import logging
from .PlantConfiguration import PlantConfiguration
from .PlantEvent import PlantEvent, PlantEventData
from ..Hardware.Sensors.Water.WaterSensor import WaterSensor, WATER_SENSOR_UNDER_WATER
import threading
from ..Utils.WakeableSleep import WakeableSleep
from ..Hardware.Sensors.Plant.PlantSensor import PlantSensor

_logger = logging.getLogger(__name__)

debugMode = False

def IsDebugMode() -> bool:
    global debugMode
    return debugMode

def SetDebugMode(value : bool) -> None:
    global debugMode
    debugMode = value

class PlantManager:

    __staticId : int = 0
    __batterLowLevel : int = 5
    __consecutivePolls : int = 1 #try to use criticalInterval instead (so no DoS happens)
    __maximumSleepingTime : int = 5 #for threads waking up to check if manager is still running

    def __init__(self, waterSensor : WaterSensor, plants : list[Plant] = []) -> None:
        self.__id : int = PlantManager.__staticId + 1
        PlantManager.__staticId = PlantManager.__staticId + 1
        self.__logger : logging.Logger = _logger.getChild("PlantManager" + str(self.__id))
        self.__logger.info("Initializing plant manager...")
        self.__sensorsLock : threading.Lock = threading.Lock()
        self.__sensors : dict[PlantSensor, list[Plant]] = {} #plants sorted after sensors
        self.__errorsLock : threading.Lock = threading.Lock()
        self.__errors : dict[Plant, dict[str, float]] = {} #errors for each plant
        self.__criticalInterval : float = 900 #15 min #time that needs to pass in order for an error to be regarded as critical (action needed)
        self.__pollInterval : float = 300 #5min
        self.__sensorDataCacheLock : threading.Lock = threading.Lock()
        self.__sensorDataCache : dict[PlantSensor, dict[str, object]] = {}
        self.__lastPollUpdate : float = -1
        self.__lastActionUpdate : float = -1

        self.__onWaterError : dict[PlantSensor, PlantEvent] = {}
        #self.__onWaterError += PlantManager.ErrorFixByWateringPlant

        self.__onBatteryError : dict[PlantSensor, PlantEvent] = {}
        #self.__onBatteryError += PlantManager.ErrorFixByEmail

        self.__onConductivityError : dict[PlantSensor, PlantEvent] = {}
        #self.__onConductivityError += PlantManager.ErrorFixByEmail

        self.__onTemperatureError : dict[PlantSensor, PlantEvent] = {}
        #self.__onTemperatureError += PlantManager.ErrorFixByEmail

        self.__onLightError : dict[PlantSensor, PlantEvent] = {}
        #self.__onLightError += PlantManager.ErrorFixByEmail

        self.__waterSensor : WaterSensor = waterSensor
        self.__isRunning : bool = False
        self.__actionThread : threading.Thread = None
        self.__pollThread : threading.Thread = None
        self.__cancellationToken : threading.Event = None
        self.__startedInDebugMode : bool = False

        for plant in plants:
            self.Add(plant)
        self.__logger.debug("Plant manager successfully initialized")

    @property
    def PollInterval(self) -> int:
        return self.__pollInterval    
        
    @PollInterval.setter
    def PollInterval(self, value : int) -> None:
        self.__pollInterval = value
    
    @property
    def CriticalInterval(self) -> int:
        return self.__criticalInterval

    @CriticalInterval.setter
    def CriticalInterval(self, value : int) -> None:
        self.__criticalInterval = value

    #TODO setter needed for "+= eventhandler"
    def GetOnWaterError(self, plantSensor : PlantSensor) -> None:
        return self.__onWaterError[plantSensor]

    def GetOnBatteryError(self, plantSensor : PlantSensor) -> None:
        return self.__onBatteryError[plantSensor]

    def GetOnConductivityError(self, plantSensor : PlantSensor) -> None:
        return self.__onConductivityError[plantSensor]

    def GetOnTemperatureError(self, plantSensor : PlantSensor) -> None:
        return self.__onTemperatureError[plantSensor]

    def GetOnLightError(self, plantSensor : PlantSensor) -> None:
        return self.__onLightError[plantSensor]

    @property
    def WaterSensor(self) -> WaterSensor:
        return self.__waterSensor

    @property
    def IsRunning(self) -> bool:
        return self.__isRunning

    @property
    def IsDebug(self) -> bool:
        global debugMode
        return (debugMode and not self.IsRunning) or self.__startedInDebugMode
    
    @property
    def Plants(self) -> list[Plant]:
        plants = []
        with self.__sensorsLock:
            for sensor in self.__sensors:
                sensorPlants = self.__sensors[sensor]
                for plant in sensorPlants:
                    plants.append(plant)
        return plants

    @property
    def Sensors(self) -> list[PlantSensor]:
        sensors = []
        with self.__sensorsLock:
            sensors = list(self.__sensors.keys())
        return sensors
        
    @property
    def Pumps(self) -> list[Pump]:
        pumps = []
        plants = self.Plants

        for plant in plants:
            if plant.Pump != None and not plant.Pump in pumps:
                pumps.append(plant.Pump)

        return pumps

    def Add(self, plant : Plant) -> None:
        self.__logger.debug("Adding plant " + plant.PlantConfiguration.Name + " to plant manager...")
        plants = self.Plants
        if plant not in plants:
            with self.__sensorsLock:
                if not plant.PlantSensor in self.__sensors:
                    self.__sensors[plant.PlantSensor] = []

                    self.__onWaterError[plant.PlantSensor] = PlantEvent()
                    self.__onBatteryError[plant.PlantSensor] = PlantEvent()
                    self.__onConductivityError[plant.PlantSensor] = PlantEvent()
                    self.__onTemperatureError[plant.PlantSensor] = PlantEvent()
                    self.__onLightError[plant.PlantSensor] = PlantEvent()
                
                self.__sensors[plant.PlantSensor].append(plant)

                plant.AddOnPlantChangedEventHandler(self.__onPlantChanged)

            with self.__errorsLock:
                self.__errors[plant] = {}

            self.__logger.info("Successfully added plant " + plant.PlantConfiguration.Name + " to plant manager")
        else:
            self.__logger.critical("Could not add " + plant.PlantConfiguration.Name + " to plant manager, because it already exists")

    def Remove(self, plant : Plant) -> None:
        self.__logger.debug("Removing plant " + plant.PlantConfiguration.Name + " from plant manager")
        with self.__sensorsLock:
            if plant.PlantSensor in self.__sensors:
                self.__sensors[plant.PlantSensor].remove(plant)
                if len(self.__sensors[plant.PlantSensor]) == 0:
                    self.__sensors.pop(plant.PlantSensor)
                        
                    self.__onWaterError.pop(plant.PlantSensor)
                    self.__onBatteryError.pop(plant.PlantSensor)
                    self.__onConductivityError.pop(plant.PlantSensor)
                    self.__onTemperatureError.pop(plant.PlantSensor)
                    self.__onLightError.pop(plant.PlantSensor)
            plant.RemoveOnPlantChangedEventHandler(self.__onPlantChanged)

        with self.__errorsLock:
            self.__errors.pop(plant)

        self.__logger.info("Successfully removed plant " + plant.PlantConfiguration.Name + " from plant manager")

    def Start(self) -> None:
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

    def Stop(self) -> None:
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

    def UpdatePoll(self) -> None:
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
                errorDict : dict[str,float] = {}
                plantString = ""
                dataString = ""
                errorString = ""

                for x in data:
                    dataString += x + ": " + str(data[x]) + ", "
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
                    
                    with self.__errorsLock:
                        #check if errors still persist (else delete)
                        for oldErrorKey in self.__errors[plants[x]]:
                            for newErrorKey in errorDict:
                                if newErrorKey == oldErrorKey:
                                    #error persists
                                    break
                            else:
                                self.__errors[plants[x]][oldErrorKey] = None
                        #add new errors
                        for newErrorKey in errorDict:
                            if not newErrorKey in self.__errors[plants[x]]:
                                self.__errors[plants[x]][newErrorKey] = t

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
                self.__logger.info("Poll time for plant manager: "   + str(timeNeeded) + "s")
                self.__logger.debug("Plant manager finished poll with " + str(abs(nextPollIn)) + "s delay")
            else:
                self.__logger.info("Poll time for plant manager: " + str(timeNeeded) + "s, sleeping now for next poll in: " + str(nextPollIn) + "s")
                self.__logger.debug("Poll thread resuming after " + str(WakeableSleep(self.__cancellationToken, nextPollIn, PlantManager.__maximumSleepingTime)) + "s")


        if self.__cancellationToken.is_set():
            self.__logger.debug("Poll thread finished")
        else:
            self.__logger.warning("Poll thread closed unexpectedly")
    
    def UpdateAction(self) -> None:
        #sleep for first time
        WakeableSleep(self.__cancellationToken,self.__criticalInterval)
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
                errors : dict[str, dict[Plant, float]] = {}
                sensorData : dict[str, object] = {}
                with self.__sensorDataCacheLock:
                    sensorData = self.__sensorDataCache[sensor]

                #filter for critical errors
                #foreach plant from the same sensor
                for plant in plants:
                    for error in currentErrors[plant]:
                        errorTime = currentErrors[plant][error]
                        if t >= errorTime + self.__criticalInterval:
                            if not error in errors:
                                errors[error] = {}
                            errors[error][plant] = errorTime
                        else:
                            #no action needed
                            pass
                if self.__cancellationToken.is_set():
                    break

                for error in errors:
                    errorPlants = errors[error]
                    if error == PSP.BATTERY:
                        self.__logger.debug("Plant manager fixing low battery on [" + sensor.ID + "]...")
                        if len(self.__onBatteryError[sensor]) > 0:
                            self.__onBatteryError[sensor](PlantEventData(self, plants, sensorData, error, errorPlants, self.__logger))
                        else:
                            self.__logger.critical("Plant manager can not fix battery")
                    elif error == PSP.CONDUCTIVITY:
                        self.__logger.debug("Plant manager fixing conductivity on [" + sensor.ID + "]...")
                        if len(self.__onConductivityError[sensor]) > 0:
                            self.__onConductivityError[sensor](PlantEventData(self, plants, sensorData, error, errorPlants, self.__logger))
                        else:
                            self.__logger.critical("Plant manager can not fix conductivity")
                    elif error == PSP.LIGHT:
                        self.__logger.debug("Plant manager fixing light on [" + sensor.ID + "]...")
                        if len(self.__onLightError[sensor]) > 0:
                            self.__onLightError[sensor](PlantEventData(self, plants, sensorData, error, errorPlants, self.__logger))
                        else:
                            self.__logger.critical("Plant manager can not fix light")
                    elif error == PSP.MOISTURE:
                        self.__logger.debug("Plant manager fixing moisture on [" + sensor.ID + "]...")
                        if len(self.__onWaterError[sensor]) > 0:
                            self.__onWaterError[sensor](PlantEventData(self, plants, sensorData, error, errorPlants, self.__logger))
                        else:
                            self.__logger.critical("Plant manager can not fix moisture")
                    elif error == PSP.TEMPERATURE:
                        self.__logger.debug("Plant manager fixing temperature on [" + sensor.ID + "]...")
                        if len(self.__onTemperatureError[sensor]) > 0:
                            self.__onTemperatureError[sensor](PlantEventData(self, plants, sensorData, error, errorPlants, self.__logger))
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
                self.__logger.info("Plant manager finished fixing round in " + str(timeNeeded) + "s")
                self.__logger.debug("Plant manager finished fixing round with " + str(abs(nextFixIn)) + "s delay")
            else:
                self.__logger.info("Plant manager finished fixing round in " + str(timeNeeded) + "s, sleeping now for next fixing round in: " + str(nextFixIn) + "s")
                self.__logger.debug("Action thread resuming after " + str(WakeableSleep(self.__cancellationToken, nextFixIn, PlantManager.__maximumSleepingTime)) + "s")
        if self.__cancellationToken.is_set():
            self.__logger.debug("Action thread finished")
        else:
            self.__logger.warning("Action thread closed unexpectedly")

    def ErrorFixByEmail(plantEventData : PlantEventData) -> None:
        #TODO
        plantEventData.Logger.critical("Could not send email: Not Implemented")

    def ErrorFixByWateringPlant(plantEventData : PlantEventData) -> None:
        #TODO create errorPlantString for logging
        #TODO check if error is because underwatering else log info
        if plantEventData.Error == PSP.MOISTURE:
            #merge all different pumps by plants
            pumpPlants : dict[Pump, list[Plant]] = {}
            for plant in plantEventData.Plants:
                if pumpPlants[plant.Pump] != None:
                    pumpPlants[plant.Pump].append(plant)
                else:
                    pumpPlants[plant.Pump] = []
                    pumpPlants[plant.Pump].append(plant)

            #TODO if all error plants have a pump assigned in pumpPlants, else logger.critical("Could not water " + plantEventData.Plant.PlantConfiguration.Name + ", because there is no pump configured")
            for pump in pumpPlants:

                #get minimal maximum water and maximal minimum water for all plants
                maximumWater = -1
                minimumWater = -1
                for plant in pumpPlants[pump]:
                    if maximumWater == -1 or maximumWater > plant.PlantConfiguration.MoistureSpan.Max:
                        maximumWater = plant.PlantConfiguration.MoistureSpan.Max

                    if minimumWater == -1 or minimumWater < plant.PlantConfiguration.MoistureSpan.Min:
                        minimumWater = plant.PlantConfiguration.MoistureSpan.Min

                if maximumWater >= minimumWater and maximumWater > 0:
                    waterNeeded = maximumWater - plantEventData.SensorData[PSP.MOISTURE]
                    if waterNeeded > 0:
                        if plantEventData.PlantManager.WaterSensor.PollSensor()[WATER_SENSOR_UNDER_WATER]:
                            for plant in pumpPlants[pump]:
                                plantEventData.Logger.debug("Watering " + plant.PlantConfiguration.Name + " with " + str(waterNeeded) + "ml")
                                waterGiven = pump.Water(waterNeeded)
                                plantEventData.Logger.info("Successfully watered " + plant.PlantConfiguration.Name + " with " + str(waterGiven) + "ml")
                                plantEventData.Logger.debug("Water difference of " + plant.PlantConfiguration.Name + " is " + str(waterGiven - waterNeeded) + "ml")
                        else:
                            plantEventData.Logger.critical("Could not water with " + str(pump.ID) + ", because there is not enough water left")
                    else:
                        plantEventData.Logger.warning("Could not water with " + str(pump.ID) + ", because other plants could be overwatered")
                else:
                    plantEventData.Logger.critical("Could not water with " + str(pump.ID) + ", because the setup does not allow it (Minimum needed water: " + str(minimumWater) + ", Maximum needed water: " + str(maximumWater) + ")")
        else:
            plantEventData.Logger.warning("FAILSAFE: Not watering, because error type was " + plantEventData.Error + " instead of " + PSP.MOISTURE)

    def __onPlantChanged(self, plant : Plant, oldValue : object, newValue : object, type : str) -> None:
        if type == Plant.EVENTTYPE_PLANTSENSOR:
            newValue.__class__ = PlantSensor
            oldValue.__class__ = PlantSensor
            if oldValue != newValue:
                with self.__sensorsLock:
                    #delete old sensor
                    if oldValue in self.__sensors:
                        if len(self.__sensors[oldValue]) > 1:
                            self.__sensors[oldValue].remove(plant)
                        else:
                            self.__sensors.pop(oldValue)
                                
                            self.__onWaterError.pop(oldValue)
                            self.__onBatteryError.pop(oldValue)
                            self.__onConductivityError.pop(oldValue)
                            self.__onTemperatureError.pop(oldValue)
                            self.__onLightError.pop(oldValue)

                    #add new sensor
                    if not newValue in self.__sensors:
                        self.__sensors[newValue] = []

                    self.__sensors[newValue].append(plant)

                    self.__onWaterError[newValue] = PlantEvent()
                    self.__onBatteryError[newValue] = PlantEvent()
                    self.__onConductivityError[newValue] = PlantEvent()
                    self.__onTemperatureError[newValue] = PlantEvent()
                    self.__onLightError[newValue] = PlantEvent()
                    
        elif type == Plant.EVENTTYPE_PLANTCONFIGURATION:
            newValue.__class__ = PlantConfiguration            
            oldValue.__class__ = PlantConfiguration

            if oldValue.Name != newValue.Name:
                for p in self.Plants:
                    if newValue.Name == p.PlantConfiguration.Name and p != plant:
                        raise ValueError("Plant with name " + str(newValue.Name) + " already exists")