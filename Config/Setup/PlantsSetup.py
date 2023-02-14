import json
import re
import os
from .InitialSetup import NOERRORRESPONSE, ROOTFILE, ListVirtualFiles, ONLOAD, ONSAVE, ONCLOSE, ONINIT
from .GPIOSetup import GPIOMANAGER
from Home.Hardware.Actors.Water.Pump import Pump
from Home.Hardware.Actors.Water.GPIOPump import GPIOPump
from Home.Hardware.GPIOManager import GPIOTypes
from Home.Hardware.Sensors.Water.AlwaysActiveWaterSensor import AlwaysActiveWaterSensor
from Home.Webserver.VirtualFile import METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from Home.Hardware.BluetoothManager import BluetoothManager
from Home.Plants.PlantManager import PlantManager
import Home.Plants.PlantManager as PM
from Home.Plants.Plant import Plant
from Home.Plants.PlantConfiguration import PlantConfiguration
from Home.Hardware.Sensors.Plant.PlantSensor import PlantSensor
from Home.Hardware.Sensors.Plant.MiFloraPlantSensor import MiFloraPlantSensor
import Home.Hardware.Sensors.Plant.MiFloraPlantSensor as MiFloraPS
from Home.Utils.ValueSpan import ValueSpan

PLANTMANAGER = PlantManager(AlwaysActiveWaterSensor())


def __plantmanagerStatus(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    data = {}
    data["running"] = False
    data["debug"] = False
    data["error"] = NOERRORRESPONSE
    
    if PLANTMANAGER != None:
        data["running"] = PLANTMANAGER.IsRunning
        data["debug"] = PLANTMANAGER.IsDebug
    else:
        data["error"] = {
            "set": True,
            "message": "Plantmanager not defined"
        }
    return json.dumps(data)

def __plantmanagerSwitch(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    if PLANTMANAGER != None:
        if "running" in request.GetParameters:
            value = str(request.GetParameters["running"][0])
            if "true" == value:
                PLANTMANAGER.Start()
            elif "false" == value:
                PLANTMANAGER.Stop()
        if "debug" in request.GetParameters:
            value = str(request.GetParameters["debug"][0])
            if PLANTMANAGER.IsDebug and not value:
                PM.debugMode = value
                #for plant in PLANTMANAGER.Plants:
                    #TODO Upgrade Sensors to non debug
                #    pass
                if PLANTMANAGER.IsRunning:
                    PLANTMANAGER.Stop()
                    PLANTMANAGER.Start()

    return __plantmanagerStatus(file, request)

def __plantmanagerPlants(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    plants = {}
    plants["plants"] = [] #type:list[Plant]
    plants["error"] = NOERRORRESPONSE

    if PLANTMANAGER != None:
        for plant in PLANTMANAGER.Plants:
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

def __addPlant(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    output = {}
    output["error"] = NOERRORRESPONSE
    if not PLANTMANAGER.IsRunning:
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
            for s in PLANTMANAGER.Sensors:
                #TODO optimize
                if data["sensor"]["id"] == s.ID and data["sensor"]["type"] == s.__class__.__name__:
                    sensor = s
                    break
            else:        
                if str(data["sensor"]["type"]) == MiFloraPlantSensor.__name__:
                    for sens in BluetoothManager.GetFilteredAvailableDevices("[Ff]lower[ ]*[Cc]are"):
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
            for p in PLANTMANAGER.Pumps:
                #TODO optimize
                if str(data["pump"]["id"]) == p.ID and str(data["pump"]["type"]) == p.__class__.__name__:
                    pump = p
                    break
            else:
                if str(data["pump"]["type"]) == GPIOPump.__name__:
                    for gpio in GPIOMANAGER.GetAvailableGPIOs():
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
            for p in PLANTMANAGER.Plants:
                if plantConfiguration.Name == p.PlantConfiguration.Name:
                    alreadyExists = True
                    break

            if not alreadyExists:
                PLANTMANAGER.Add(Plant(plantConfiguration, {
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
def __changePlant(file, request):
#type: (VirtualFile, ServerRequest) -> str
    output = {}
    output["error"] = NOERRORRESPONSE
    if not PLANTMANAGER.IsRunning:
        data = json.loads(request.Data)

        plant = None #type: Plant
        if "filter" in request.GetParameters:
            found = False
            value = str(request.GetParameters["filter"][0])
            for p in PLANTMANAGER.Plants:
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
                        for p in PLANTMANAGER.Plants:
                            if p.PlantConfiguration.Name == plantConfiguration.Name:
                                output["error"] = {
                                    "set": True,
                                    "message": "Plant " + plantConfiguration.Name + " already exists"
                                }

                    if not output["error"]["set"]:
                        #get or create sensor
                        for s in PLANTMANAGER.Sensors:
                            #TODO optimize
                            if data["sensor"]["id"] == s.ID and str(data["sensor"]["type"]) == s.__class__.__name__:
                                sensor = s
                                break
                        else:        
                            if str(data["sensor"]["type"]) == MiFloraPlantSensor.__name__:
                                for sens in BluetoothManager.GetFilteredAvailableDevices("[Ff]lower[ ]*[Cc]are"):
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
                        for p in PLANTMANAGER.Pumps:
                            #TODO optimize
                            if data["pump"]["id"] == p.ID and str(data["pump"]["type"]) == p.__class__.__name__:
                                pump = p
                                break
                        else:
                            if str(data["pump"]["type"]) == GPIOPump.__name__:
                                for gpio in GPIOMANAGER.GetAvailableGPIOs():
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

def __deletePlant(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    output = {}
    output["error"] = NOERRORRESPONSE
    if not PLANTMANAGER.IsRunning:
        plant = None #type: Plant
        if "filter" in request.GetParameters:
            found = False
            value = str(request.GetParameters["filter"][0])

            for p in PLANTMANAGER.Plants:
                if re.match(value,p.PlantConfiguration.Name):
                    plant = p
                    found = True
                    break
            if found:
                PLANTMANAGER.Remove(plant)
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

##################################Plants##################################
PLANTSERVICE = ROOTFILE.AddNewChildFile("plantmanagerservice")
PLANTSERVICE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,ListVirtualFiles))

PLANTMANAGERSTATUS = PLANTSERVICE.AddNewChildFile("status")
PLANTMANAGERSTATUS.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__plantmanagerStatus))

PLANTMANAGERSWITCH = PLANTSERVICE.AddNewChildFile("switch")
PLANTMANAGERSWITCH.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__plantmanagerSwitch))

PLANTMANAGERPLANTS = PLANTSERVICE.AddNewChildFile("plants")
PLANTMANAGERPLANTS.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__plantmanagerPlants))

PLANTMANAGERADDPLANT = PLANTMANAGERPLANTS.AddNewChildFile("add")
PLANTMANAGERADDPLANT.Bind(VirtualFileHandler(METHOD_POST, TYPE_JSONFILE,__addPlant))

PLANTMANAGERCHANGEPLANT = PLANTMANAGERPLANTS.AddNewChildFile("change")
PLANTMANAGERCHANGEPLANT.Bind(VirtualFileHandler(METHOD_POST, TYPE_JSONFILE,__changePlant))

PLANTMANAGERDELETEPLANT = PLANTMANAGERPLANTS.AddNewChildFile("delete")
PLANTMANAGERDELETEPLANT.Bind(VirtualFileHandler(METHOD_POST, TYPE_JSONFILE,__deletePlant))

__plantsSaveFile = "plants.json"

#TODO valid JSON-formatting
def Save(saveDirectory):
    if not PLANTMANAGER.IsDebug:
        saveDirectory = saveDirectory.rstrip("/").rstrip("\\")
        #type: (str) -> None
        data = []
        plants = PLANTMANAGER.Plants
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

        file = open(saveDirectory + "/" + __plantsSaveFile, 'w')
        file.writelines(data)
        file.close()


def Load(saveDirectory):
    #type: (str) -> None
    saveDirectory = saveDirectory.rstrip("/").rstrip("\\")
    file = saveDirectory + "/" + __plantsSaveFile
    if os.path.exists(file) and os.path.isfile(file):
        data = []
        file = open(saveDirectory + "/" + __plantsSaveFile, 'r')
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
                    gpios = GPIOMANAGER.GetFilteredAvailableGPIOs(GPIOTypes.STANDARDINOUT)
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
            PLANTMANAGER.Add(Plant(pc,{
                Plant.HARDWARE_PUMP: currentPump,
                Plant.HARDWARE_PLANTSENSOR: currentSensor,
            }))
def onClose():
    if PLANTMANAGER != None and PLANTMANAGER.IsRunning:
        PLANTMANAGER.Stop()

def onInit(debug : bool):
    PM.debugMode = MiFloraPS.debugMode or debug

ONLOAD += Load
ONSAVE += Save
ONCLOSE += onClose
ONINIT += onInit