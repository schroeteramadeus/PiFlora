import json
import re
from .InitialSetup import NOERRORRESPONSE, ROOTFILE, ListVirtualFiles, ONSAVE, ONLOAD, ONCLOSE, ONINIT
from Home.Webserver.VirtualFile import METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from Home.Hardware.BluetoothManager import BluetoothManager
import Home.Hardware.BluetoothManager as BM
from Home.Hardware.Sensors.Plant.MiFloraPlantSensor import MiFloraPlantSensor as MiFloraPlantSensor

BLUETOOTHMANAGER = BluetoothManager

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

def onClose():
    if BLUETOOTHMANAGER != None and BLUETOOTHMANAGER.IsRunning():
        BLUETOOTHMANAGER.Stop()

def onInit(debug : bool):
    BM.debugMode = debug or BM.debugMode

ONLOAD += Load
ONSAVE += Save
ONCLOSE += onClose
ONINIT += onInit