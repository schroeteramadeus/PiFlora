import json
import re
import sys
import traceback
from urllib.parse import ParseResult, parse_qs
from Home.Hardware.Actors.Water.Pump import Pump
from Home.Hardware.Actors.Water.GPIOPump import GPIOPump
from Home.Hardware.GPIOManager import GPIOManager, GPIOTypes
from Home.Hardware.Sensors.Water.AlwaysActiveWaterSensor import AlwaysActiveWaterSensor
from Home.Webserver.VirtualFile import METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from Home.Hardware.BluetoothManager import BluetoothManager
import Home.Hardware.BluetoothManager as BM
from Home.Plants.PlantManager import PlantManager
import Home.Plants.PlantManager as PM
from Home.Plants.Plant import Plant
from Home.Plants.PlantConfiguration import PlantConfiguration
from Home.Hardware.Sensors.Plant.PlantSensor import PlantSensor, PlantSensorParameters as PSP
from Home.Hardware.Sensors.Plant.MiFloraPlantSensor import debugMode as MiFloraDebugMode, MiFloraPlantSensor as MiFloraPlantSensor
from Home.Utils.ValueSpan import ValueSpan

STANDARDPATH = "index.html"

HOSTNAME = "localhost"
SERVERPORT = 8080
TITLE = "Home"
SERVEABLEFILEEXTENSIONS = (".html", ".htm", ".ico", ".png", ".jpeg", ".jpg", ".gif", ".tiff", ".ttf", ".woff2", ".js", ".ts", ".css", ".min")

if MiFloraDebugMode:
    PM.debugMode = True

PLANTMANAGER = PlantManager(AlwaysActiveWaterSensor())

BLUETOOTHMANAGER = BluetoothManager
GPIOMANAGER = GPIOManager

NOERRORRESPONSE = {
    "set": False,
    "message": None
}
def __listVirtualFiles(file, request):
    #type: (VirtualFile, ServerRequest) -> str

    html = "<!DOCTYPE html><html>"
    head = ""
    body = "<h1>Files in " + file.FullPath + "</h1><ul>"

    for f in file.GetAllFiles():
        interactiveString = ""
        if f.HasMethodHandler(METHOD_GET):
            handler = f.GetMethodHandler(METHOD_GET)
            if handler.Type == TYPE_HTMLFILE:
                interactiveString = "(HTML)"
            elif handler.Type == TYPE_JSONFILE:
                interactiveString = "(JSON)"
            else:
                interactiveString = "(other)"

        body += "<li><a href='" + f.FullPath + "'>" + f.Name + interactiveString + "</a></li>"
    
    body += "</ul>"

    html += "<head>" + head + "</head><body>" + body + "</body></html>"
    return html
    
def __bluetoothServiceStatus(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    data = {}
    data["running"] = False
    data["debug"] = False
    data["error"] = NOERRORRESPONSE
    if BLUETOOTHMANAGER != None:
        data["running"] = BLUETOOTHMANAGER.IsRunning()
        data["debug"] = BLUETOOTHMANAGER.IsDebug()
    else:
        data["error"] = {
            "set": True,
            "message": "Bluetoothmanager not defined"
        }
    return json.dumps(data)

def __bluetoothServiceSwitch(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    
    if BLUETOOTHMANAGER != None:
        if "running" in request.GetParameters:
            value = str(request.GetParameters["running"][0])
            if "true" == value:
                BLUETOOTHMANAGER.Start()
            elif "false" == value:
                BLUETOOTHMANAGER.Stop()
        if "debug" in request.GetParameters:
            value = str(request.GetParameters["debug"][0])
            if BLUETOOTHMANAGER.IsDebug() and not value:
                BM.debugMode = value
                if BLUETOOTHMANAGER.IsRunning():
                    BLUETOOTHMANAGER.Stop()
                    BLUETOOTHMANAGER.Start()

    return __bluetoothServiceStatus(file, request)

def __getBluetoothDevices(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    data = {}
    data["error"] = NOERRORRESPONSE
    if BLUETOOTHMANAGER != None:
        if "filter" in request.GetParameters:
            value = str(request.GetParameters["filter"][0])
            data["devices"] = BLUETOOTHMANAGER.GetFilteredAvailableDevices(value)
        else:
            data["devices"] = BLUETOOTHMANAGER.GetAvailableDevices()
    else:
        data["error"] = {
            "set": True,
            "message": "Bluetoothmanager not defined"
        }

    return json.dumps(data)

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
            "message": "Bluetoothmanager not defined"
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
                PLANTMANAGER.Remove(plant)
            else:
                output["error"] = {
                    "set": True,
                    "message": "Plant not known",
                }

    return output


def __getAllGPIOs(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    data = {}
    data["gpios"] = []

    gpios = []

    data["error"] = NOERRORRESPONSE
    if GPIOMANAGER != None:
        if "filter" in request.GetParameters:
            value = str(request.GetParameters["filter"][0])
            for t in GPIOTypes.GetAll():
                if value == t.Name:
                    gpios = GPIOMANAGER.GetFilteredGPIOs(t)
        else:
            gpios = GPIOMANAGER.GetAllGPIOs()
    else:
        data["error"] = {
            "set": True,
            "message": "GPIOManager not defined"
        }

    for gpio in gpios:
        data["gpios"].append({
            "port": gpio.Port,
            "type": gpio.Type.Name,
        })

    return json.dumps(data)

def __getAvailableGPIOs(file, request):
    #type: (VirtualFile, ServerRequest) -> str
    data = {}
    data["gpios"] = []

    gpios = []

    data["error"] = NOERRORRESPONSE
    if GPIOMANAGER != None:
        if "filter" in request.GetParameters:
            value = str(request.GetParameters["filter"][0])
            for t in GPIOTypes.GetAll():
                if value == t.Name:
                    gpios = GPIOMANAGER.GetFilteredAvailableGPIOs(t)
        else:
            gpios = GPIOMANAGER.GetAvailableGPIOs()
    else:
        data["error"] = {
            "set": True,
            "message": "GPIOManager not defined"
        }

    for gpio in gpios:
        data["gpios"].append({
            "port": gpio.Port,
            "type": gpio.Type.Name,
        })

    return json.dumps(data)

ROOTFILE = VirtualFile(None, "root")
ROOTFILE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,__listVirtualFiles))

##################################Plants##################################
PLANTSERVICE = ROOTFILE.AddNewChildFile("plantmanagerservice")
PLANTSERVICE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,__listVirtualFiles))

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

##################################Bluetooth##################################
BLUETOOTHSERVICE = ROOTFILE.AddNewChildFile("bluetoothservice")
BLUETOOTHSERVICE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,__listVirtualFiles))

BLUETOOTHSERVICESTATUS = BLUETOOTHSERVICE.AddNewChildFile("status")
BLUETOOTHSERVICESTATUS.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__bluetoothServiceStatus))

BLUETOOTHSERVICESWITCH = BLUETOOTHSERVICE.AddNewChildFile("switch")
BLUETOOTHSERVICESWITCH.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__bluetoothServiceSwitch))

BLUETOOTHSERVICEDEVICES = BLUETOOTHSERVICE.AddNewChildFile("devices")
BLUETOOTHSERVICEDEVICES.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__getBluetoothDevices))

##################################GPIO##################################
GPIOSERVICE = ROOTFILE.AddNewChildFile("gpioservice")
GPIOSERVICE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,__listVirtualFiles))

GPIOSERVICEGPIOS = GPIOSERVICE.AddNewChildFile("gpios")
GPIOSERVICEGPIOS.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,__listVirtualFiles))

GPIOSERVICEGPIOSAVAILABLE = GPIOSERVICEGPIOS.AddNewChildFile("available")
GPIOSERVICEGPIOSAVAILABLE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,__getAvailableGPIOs))

GPIOSERVICEGPIOSAVAILABLE = GPIOSERVICEGPIOS.AddNewChildFile("all")
GPIOSERVICEGPIOSAVAILABLE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,__getAllGPIOs))


def Save(filePath):
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

    file = open(filePath, 'w')
    file.writelines(data)
    file.close()


def Load(filePath):
    #type: (str) -> PlantManager
    data = []
    file = open(filePath, 'r')
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