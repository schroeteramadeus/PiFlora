import json
import re
from .InitialSetup import NOERRORRESPONSE, ROOTFILE, ListVirtualFiles, ONLOAD, ONSAVE, ONCLOSE, ONINIT
from Home.Hardware.GPIOManager import GPIOManager, GPIOTypes
from Home.Webserver.VirtualFile import METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from Home.Hardware.Sensors.Plant.MiFloraPlantSensor import MiFloraPlantSensor as MiFloraPlantSensor

GPIOMANAGER = GPIOManager

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

def onClose():
    pass

def onInit(debug : bool):
    pass

ONLOAD += Load
ONSAVE += Save
ONCLOSE += onClose
ONINIT += onInit