import json
import re
from .InitialSetup import BLUETOOTHMANAGER, NOERRORRESPONSE, ROOTFILE, ListVirtualFiles, ONSAVE, ONLOAD
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

BLUETOOTHSERVICE = ROOTFILE.AddNewChildFile("bluetoothservice")
BLUETOOTHSERVICE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,ListVirtualFiles))

BLUETOOTHSERVICESTATUS = BLUETOOTHSERVICE.AddNewChildFile("status")
BLUETOOTHSERVICESTATUS.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__bluetoothServiceStatus))

BLUETOOTHSERVICESWITCH = BLUETOOTHSERVICE.AddNewChildFile("switch")
BLUETOOTHSERVICESWITCH.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__bluetoothServiceSwitch))

BLUETOOTHSERVICEDEVICES = BLUETOOTHSERVICE.AddNewChildFile("devices")
BLUETOOTHSERVICEDEVICES.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,__getBluetoothDevices))

def Save(filePath):
    #type: (str) -> None
    pass


def Load(filePath):
    #type: (str) -> None
    pass

ONLOAD += Load
ONSAVE += Save