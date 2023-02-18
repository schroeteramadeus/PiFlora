import json
import re
import os
from .InitialSetup import ServerModule, SystemModule
from .GPIOSetup import GPIOModule
from .BluetoothSetup import BluetoothModule
from ....Hardware.Actors.Water.Pump import Pump
from ....Hardware.Actors.Water.GPIOPump import GPIOPump
from ....Hardware.GPIOManager import GPIOTypes
from ....Hardware.Sensors.Water.AlwaysActiveWaterSensor import AlwaysActiveWaterSensor
from ...VirtualFile import METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from ....Plants.PlantManager import PlantManager, IsDebugMode as PlantManagerIsDebugMode, SetDebugMode as PlantManagerSetDebugMode
from ....Plants.Plant import Plant
from ....Plants.PlantConfiguration import PlantConfiguration
from ....Hardware.Sensors.Plant.PlantSensor import PlantSensor
from ....Hardware.Sensors.Plant.MiFloraPlantSensor import MiFloraPlantSensor, IsDebugMode as MiFloraIsDebugMode, SetDebugMode as MiFloraSetDebugMode
from ....Utils.ValueSpan import ValueSpan

class PlantModule(ServerModule):
    def __init__(self) -> None:
        if PlantModule.TryGet() == None:
            super().__init__()
            self.__plantManager = None #type: PlantManager
            self.__systemModule = None #type: SystemModule
            self.__bluetoothModule = None #type: BluetoothModule
            self.__gpioModule = None #type: GPIOModule
            self.__plantsSaveFile = "plants.json"

    def OnSave(self, saveFolderPath : str) -> None:
        #TODO save Plantmanager metadata
        #TODO use valid json
        if not self.__plantManager.IsDebug:
            saveFolderPath = saveFolderPath.rstrip("/").rstrip("\\")
            #type: (str) -> None
            data = []
            plants = self.__plantManager.Plants
            for plant in plants:
                content = {
                    "configuration":{
                        "name": plant.PlantConfiguration.Name,
                        "temperature":{
                            "min": plant.PlantConfiguration.TemperatureSpan.Min,
                            "max": plant.PlantConfiguration.TemperatureSpan.Max,
                        },
                        "moisture":{
                            "min": plant.PlantConfiguration.MoistureSpan.Min,
                            "max": plant.PlantConfiguration.MoistureSpan.Max,
                        },
                        "light":{
                            "min": plant.PlantConfiguration.LightSpan.Min,
                            "max": plant.PlantConfiguration.LightSpan.Max,
                        },
                        "conductivity":{
                            "min": plant.PlantConfiguration.ConductivitySpan.Min,
                            "max": plant.PlantConfiguration.ConductivitySpan.Max,
                        },
                    },
                    "sensor":{
                        "id":plant.PlantSensor.ID,
                        "type": plant.PlantSensor.__class__.__name__,
                    },
                    "pump": {
                        "id": plant.Pump.ID,
                        "type": plant.Pump.__class__.__name__,
                    },
                }
                data.append(json.dumps(content) + "\n")

            file = open(saveFolderPath + "/" + self.__plantsSaveFile, 'w')
            file.writelines(data)
            file.close()
        
    def OnLoad(self, saveFolderPath : str) -> None:
        #TODO load Plantmanager metadata
        #TODO use valid json

        saveFolderPath = saveFolderPath.rstrip("/").rstrip("\\")
        file = saveFolderPath + "/" + self.__plantsSaveFile
        if os.path.exists(file) and os.path.isfile(file):
            data = []
            file = open(saveFolderPath + "/" + self.__plantsSaveFile, 'r')
            lines = file.readlines()
            
            for line in lines:
                data.append(json.loads(line))
            file.close()

            plants = [] #type: list[Plant]
            sensors = [] #type: list[PlantSensor]
            pumps = [] #type: list[Pump]

            for d in data:
                currentSensor = None
                currentPump = None
                pc = PlantConfiguration(
                    name = d["configuration"]["name"],
                    temperatureSpan = ValueSpan(int(d["configuration"]["temperature"]["min"]), int(d["configuration"]["temperature"]["max"])),
                    moistureSpan = ValueSpan(int(d["configuration"]["moisture"]["min"]), int(d["configuration"]["moisture"]["max"])),
                    lightSpan = ValueSpan(int(d["configuration"]["light"]["min"]), int(d["configuration"]["light"]["max"])),
                    conductivitySpan = ValueSpan(int(d["configuration"]["conductivity"]["min"]), int(d["configuration"]["conductivity"]["max"])),
                )
                for sensor in sensors:
                    if sensor.ID == d["sensor"]["id"]:
                        currentSensor = sensor
                        break
                else:
                    if d["sensor"]["type"] == MiFloraPlantSensor.__name__:
                        currentSensor = MiFloraPlantSensor(d["sensor"]["id"])
                        sensors.append(currentSensor)
                    else:
                        raise AttributeError("Could not deserialize sensor of type: " + d["sensor"]["type"])
                
                for pump in pumps:
                    if pump.ID == d["pump"]["id"]:
                        currentPump = pump
                        break
                else:
                    if d["pump"]["type"] == GPIOPump.__name__:
                        gpios = self.__gpioModule.GPIOManager.GetFilteredAvailableGPIOs(GPIOTypes.STANDARDINOUT)
                        for gpio in gpios:
                            if gpio.Port == int(d["pump"]["id"]):
                                currentPump = GPIOPump(gpio)
                                break
                        else:
                            raise ValueError("Could not add GPIOPump, gpio" + gpio.Port + " is not available")
                        pumps.append(currentPump)
                    #TODO add other pumps
                    else:
                        raise AttributeError("Could not deserialize pump of type: " + d["pump"]["type"])
                self.__plantManager.Add(Plant(pc,{
                    Plant.HARDWARE_PUMP: currentPump,
                    Plant.HARDWARE_PLANTSENSOR: currentSensor,
                }))
        #create new
        if self.__plantManager == None:
            self.__plantManager = PlantManager(AlwaysActiveWaterSensor())
    
    def OnClose(self) -> None:
        if self.__plantManager != None and self.__plantManager.IsRunning:
            self.__plantManager.Stop()

    def OnInit(self, debug : bool, rootFile : VirtualFile) -> None:
        self.__systemModule = SystemModule.Get()
        self.__bluetoothModule = BluetoothModule.Get()
        self.__gpioModule = GPIOModule.Get()

        PlantManagerSetDebugMode(MiFloraIsDebugMode() or debug)

        self.__plantServiceFile = rootFile.AddNewChildFile("plantmanagerservice")
        self.__plantServiceFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,self.__systemModule.ListVirtualFiles))

        self.__plantServiceStatusFile = self.__plantServiceFile.AddNewChildFile("status")
        self.__plantServiceStatusFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__plantmanagerStatus))

        self.__plantServiceSwitchFile = self.__plantServiceFile.AddNewChildFile("switch")
        self.__plantServiceSwitchFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__plantmanagerSwitch))

        self.__plantServicePlantsFile = self.__plantServiceFile.AddNewChildFile("plants")
        self.__plantServicePlantsFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__plantmanagerPlants))

        self.__plantsServiceAddPlantFile = self.__plantServicePlantsFile.AddNewChildFile("add")
        self.__plantsServiceAddPlantFile.Bind(VirtualFileHandler(METHOD_POST, TYPE_JSONFILE,self.__addPlant))

        self.__plantsServiceChangePlantFile = self.__plantServicePlantsFile.AddNewChildFile("change")
        self.__plantsServiceChangePlantFile.Bind(VirtualFileHandler(METHOD_POST, TYPE_JSONFILE,self.__changePlant))

        self.__plantsServiceDeletePlantFile = self.__plantServicePlantsFile.AddNewChildFile("delete")
        self.__plantsServiceDeletePlantFile.Bind(VirtualFileHandler(METHOD_POST, TYPE_JSONFILE,self.__deletePlant))

    def __plantmanagerStatus(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        data = {}
        data["running"] = False
        data["debug"] = False
        data["error"] = self.__systemModule.NoErrorResponse
        
        if self.__plantManager != None:
            data["running"] = self.__plantManager.IsRunning
            data["debug"] = self.__plantManager.IsDebug
        else:
            data["error"] = {
                "set": True,
                "message": "Plantmanager not defined"
            }
        return json.dumps(data)

    def __plantmanagerSwitch(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        global PlantManagerDebugMode

        if self.__plantManager != None:
            if "running" in request.GetParameters:
                value = str(request.GetParameters["running"][0])
                if "true" == value:
                    self.__plantManager.Start()
                elif "false" == value:
                    self.__plantManager.Stop()
            if "debug" in request.GetParameters:
                value = str(request.GetParameters["debug"][0])
                if self.__plantManager.IsDebug and not value:
                    PlantManagerSetDebugMode(value)
                    #for plant in PLANTMANAGER.Plants:
                        #TODO Upgrade Sensors to non debug
                    #    pass
                    if self.__plantManager.IsRunning:
                        self.__plantManager.Stop()
                        self.__plantManager.Start()

        return self.__plantmanagerStatus(file, request)

    def __plantmanagerPlants(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        plants = {}
        plants["plants"] = [] #type:list[Plant]
        plants["error"] = self.__systemModule.NoErrorResponse

        if self.__plantManager != None:
            for plant in self.__plantManager.Plants:
                if "filter" in request.GetParameters:
                    value = str(request.GetParameters["filter"][0])
                    if not re.match(value,plant.PlantConfiguration.Name):
                        continue

                data = {}
                
                data["configuration"] = {
                    "name":plant.PlantConfiguration.Name,
                    "temperature": {
                        "min":plant.PlantConfiguration.TemperatureSpan.Min,
                        "max":plant.PlantConfiguration.TemperatureSpan.Max,
                    },
                    "conductivity": {
                        "min":plant.PlantConfiguration.ConductivitySpan.Min,
                        "max":plant.PlantConfiguration.ConductivitySpan.Max,
                    },
                    "moisture": {
                        "min":plant.PlantConfiguration.MoistureSpan.Min,
                        "max":plant.PlantConfiguration.MoistureSpan.Max,
                    },
                    "light": {
                        "min":plant.PlantConfiguration.LightSpan.Min,
                        "max":plant.PlantConfiguration.LightSpan.Max,
                    },
                }
                data["sensor"] = {
                    "id": plant.PlantSensor.ID,
                    "type": plant.PlantSensor.__class__.__name__,
                }
                data["pump"] = {
                    "id": plant.Pump.ID,
                    "type": plant.Pump.__class__.__name__,
                }
                plants["plants"].append(data)
            
        else:
            plants["error"] = {
                "set": True,
                "message": "Plantmanager not defined"
            }

        return json.dumps(plants)

    def __addPlant(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        output = {}
        output["error"] = self.__systemModule.NoErrorResponse
        if not self.__plantManager.IsRunning:
            data = json.loads(request.Data)
            
            plantConfiguration = None #type: PlantConfiguration
            sensor = None #type: PlantSensor
            pump = None #type: Pump

            #TODO check vars
            try:
                plantConfiguration = PlantConfiguration(
                    name=data["configuration"]["name"],
                    temperatureSpan=ValueSpan(data["configuration"]["temperature"]["min"], data["configuration"]["temperature"]["max"]),
                    moistureSpan=ValueSpan(data["configuration"]["moisture"]["min"], data["configuration"]["moisture"]["max"]),
                    lightSpan=ValueSpan(data["configuration"]["light"]["min"], data["configuration"]["light"]["max"]),
                    conductivitySpan=ValueSpan(data["configuration"]["conductivity"]["min"], data["configuration"]["conductivity"]["max"]),
                )
                #get or create sensor
                for s in self.__plantManager.Sensors:
                    #TODO optimize
                    if data["sensor"]["id"] == s.ID and data["sensor"]["type"] == s.__class__.__name__:
                        sensor = s
                        break
                else:        
                    if str(data["sensor"]["type"]) == MiFloraPlantSensor.__name__:
                        for sens in self.__bluetoothModule.BluetoothManager.GetFilteredAvailableDevices("[Ff]lower[ ]*[Cc]are"):
                            if str(data["sensor"]["id"]) == sens["mac"]:
                                sensor = MiFloraPlantSensor(sens["mac"])
                                break
                        else:
                            output["error"] = {
                                "set": True,
                                "message": "Sensor not available"
                            }
                    #TODO add other sensorTypes?
                    else:
                        output["error"] = {
                            "set": True,
                            "message": "Sensortype not known"
                        }
                

                #get or create pump
                for p in self.__plantManager.Pumps:
                    #TODO optimize
                    if str(data["pump"]["id"]) == p.ID and str(data["pump"]["type"]) == p.__class__.__name__:
                        pump = p
                        break
                else:
                    if str(data["pump"]["type"]) == GPIOPump.__name__:
                        for gpio in self.__gpioModule.GPIOManager.GetAvailableGPIOs():
                            if int(data["pump"]["id"]) == gpio.Port and gpio.Type == GPIOTypes.STANDARDINOUT:
                                pump = GPIOPump(gpio)
                                break
                        else:
                            output["error"] = {
                                "set": True,
                                "message": "Pump not available"
                            }
                    #TODO add other pumpTypes
                    else:
                        output["error"] = {
                            "set": True,
                            "message": "Pumptype not known"
                        }
            except Exception as e:
                output["error"] = {
                    "set": True,
                    "message": "Bad formatting"
                }
            #create plant if not existant
            if not output["error"]["set"]:
                alreadyExists = False
                for p in self.__plantManager.Plants:
                    if plantConfiguration.Name == p.PlantConfiguration.Name:
                        alreadyExists = True
                        break

                if not alreadyExists:
                    self.__plantManager.Add(Plant(plantConfiguration, {
                        Plant.HARDWARE_PUMP: pump,
                        Plant.HARDWARE_PLANTSENSOR: sensor,
                    }))
                else:
                    output["error"] = {
                        "set": True,
                        "message": "Plant already exists"
                    }
        else:
            output["error"] = {
                "set": True,
                "message": "Plant is still running"
            }

        return json.dumps(output)

    #TODO allow partial changes
    def __changePlant(self, file, request):
    #type: (VirtualFile, ServerRequest) -> str
        output = {}
        output["error"] = self.__systemModule.NoErrorResponse
        if not self.__plantManager.IsRunning:
            data = json.loads(request.Data)

            plant = None #type: Plant
            if "filter" in request.GetParameters:
                found = False
                value = str(request.GetParameters["filter"][0])
                for p in self.__plantManager.Plants:
                    if re.match(value,p.PlantConfiguration.Name):
                        plant = p
                        found = True
                        break
                if found:
                    plantConfiguration = None #type: PlantConfiguration
                    sensor = None #type: PlantSensor
                    pump = None #type: Pump

                    #TODO check other vars
                    try:
                        plantConfiguration = PlantConfiguration(
                            name=str(data["configuration"]["name"]),
                            temperatureSpan=ValueSpan(data["configuration"]["temperature"]["min"], data["configuration"]["temperature"]["max"]),
                            moistureSpan=ValueSpan(data["configuration"]["moisture"]["min"], data["configuration"]["moisture"]["max"]),
                            lightSpan=ValueSpan(data["configuration"]["light"]["min"], data["configuration"]["light"]["max"]),
                            conductivitySpan=ValueSpan(data["configuration"]["conductivity"]["min"], data["configuration"]["conductivity"]["max"]),
                        )
                        if plantConfiguration.Name != plant.PlantConfiguration.Name:
                            for p in self.__plantManager.Plants:
                                if p.PlantConfiguration.Name == plantConfiguration.Name:
                                    output["error"] = {
                                        "set": True,
                                        "message": "Plant " + plantConfiguration.Name + " already exists"
                                    }

                        if not output["error"]["set"]:
                            #get or create sensor
                            for s in self.__plantManager.Sensors:
                                #TODO optimize
                                if data["sensor"]["id"] == s.ID and str(data["sensor"]["type"]) == s.__class__.__name__:
                                    sensor = s
                                    break
                            else:        
                                if str(data["sensor"]["type"]) == MiFloraPlantSensor.__name__:
                                    for sens in self.__bluetoothModule.BluetoothManager.GetFilteredAvailableDevices("[Ff]lower[ ]*[Cc]are"):
                                        if str(data["sensor"]["id"]) == sens["mac"]:
                                            sensor = MiFloraPlantSensor(sens["mac"])
                                            break
                                    else:
                                        output["error"] = {
                                            "set": True,
                                            "message": "Sensor not available"
                                        }
                                #TODO add other sensorTypes?
                                else:
                                    output["error"] = {
                                        "set": True,
                                        "message": "Sensortype not known"
                                    } 

                        if not output["error"]["set"]:
                            #get or create pump
                            for p in self.__plantManager.Pumps:
                                #TODO optimize
                                if data["pump"]["id"] == p.ID and str(data["pump"]["type"]) == p.__class__.__name__:
                                    pump = p
                                    break
                            else:
                                if str(data["pump"]["type"]) == GPIOPump.__name__:
                                    for gpio in self.__gpioModule.GPIOManager.GetAvailableGPIOs():
                                        if int(data["pump"]["id"]) == gpio.Port and gpio.Type == GPIOTypes.STANDARDINOUT:
                                            pump = GPIOPump(gpio)
                                            break
                                    else:
                                        output["error"] = {
                                            "set": True,
                                            "message": "Pump not available"
                                        }
                                #TODO add other pumpTypes
                                else:
                                    output["error"] = {
                                        "set": True,
                                        "message": "Pumptype not known"
                                    }
                    except Exception as e:
                        output["error"] = {
                            "set": True,
                            "message": "Bad formatting"
                        }

                    #change plant, delete unnecessary pumps and sensors
                    if not output["error"]["set"]:
                        if not plant.PlantSensor.ID == sensor.ID:
                            plant.PlantSensor = sensor
                        
                        if not plant.Pump.ID == pump.ID:
                            plant.Pump = pump

                        plant.PlantConfiguration = plantConfiguration
                else:
                    output["error"] = {
                        "set": True,
                        "message": "Plant not known",
                    }
            else:
                output["error"] = {
                    "set": True,
                    "message": "Bad formatting"
                }
        else:
            output["error"] = {
                "set": True,
                "message": "Plantmanager is still running"
            }  
        return json.dumps(output)

    def __deletePlant(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        output = {}
        output["error"] = self.__systemModule.NoErrorResponse
        if not self.__plantManager.IsRunning:
            plant = None #type: Plant
            if "filter" in request.GetParameters:
                found = False
                value = str(request.GetParameters["filter"][0])

                for p in self.__plantManager.Plants:
                    if re.match(value,p.PlantConfiguration.Name):
                        plant = p
                        found = True
                        break
                if found:
                    self.__plantManager.Remove(plant)
                else:
                    output["error"] = {
                        "set": True,
                        "message": "Plant not known",
                    }
            else:
                output["error"] = {
                    "set": True,
                    "message": "Bad formatting"
                }
        else:
            output["error"] = {
                "set": True,
                "message": "Plantmanager is still running"
            } 
            
        return json.dumps(output)

__plantModule = PlantModule()