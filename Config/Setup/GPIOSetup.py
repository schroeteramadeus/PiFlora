import json
import re
from .InitialSetup import PLANTMANAGER, BLUETOOTHMANAGER, GPIOMANAGER, NOERRORRESPONSE, ROOTFILE, ListVirtualFiles, ONLOAD, ONSAVE
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

GPIOSERVICE = ROOTFILE.AddNewChildFile("gpioservice")
GPIOSERVICE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,ListVirtualFiles))

GPIOSERVICEGPIOS = GPIOSERVICE.AddNewChildFile("gpios")
GPIOSERVICEGPIOS.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,ListVirtualFiles))

GPIOSERVICEGPIOSAVAILABLE = GPIOSERVICEGPIOS.AddNewChildFile("available")
GPIOSERVICEGPIOSAVAILABLE.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__getAvailableGPIOs))

GPIOSERVICEGPIOSAVAILABLE = GPIOSERVICEGPIOS.AddNewChildFile("all")
GPIOSERVICEGPIOSAVAILABLE.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__getAllGPIOs))


def Save(filePath):
    #type: (str) -> None
    pass


def Load(filePath):
    #type: (str) -> None
    pass

ONLOAD += Load
ONSAVE += Save