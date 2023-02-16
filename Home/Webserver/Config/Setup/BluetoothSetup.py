import json
import re
from typing import Type
from .InitialSetup import ServerModule, SystemModule
from ...VirtualFile import METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from ....Hardware.BluetoothManager import BluetoothManager, SetDebugMode as BluetoothManagerSetDebugMode, IsDebugMode as BluetoothManagerIsDebugMode
from ....Hardware.Sensors.Plant.MiFloraPlantSensor import MiFloraPlantSensor as MiFloraPlantSensor

class BluetoothModule(ServerModule):
    def __init__(self) -> None:
        super().__init__()
        self.__bluetoothManager = BluetoothManager
        self.__systemModule = None #type: SystemModule

    @property
    def BluetoothManager(self) -> Type[BluetoothManager]:
        return self.__bluetoothManager

    def OnSave(self, saveFolderPath : str) -> None:
        pass
    def OnLoad(self, saveFolderPath : str) -> None:
        pass
    def OnClose(self) -> None:
        if self.__bluetoothManager != None and self.__bluetoothManager.IsRunning():
            self.__bluetoothManager.Stop()

    def OnInit(self, debug : bool, rootFile : VirtualFile) -> None:        
        self.__systemModule = SystemModule.Get()
        
        BluetoothManagerSetDebugMode(debug or BluetoothManagerIsDebugMode())

        self.__bluetoothServiceFile = rootFile.AddNewChildFile("bluetoothservice") #type: VirtualFile
        self.__bluetoothServiceFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,self.__systemModule.ListVirtualFiles))

        self.__bluetoothServiceStatusFile = self.__bluetoothServiceFile.AddNewChildFile("status")
        self.__bluetoothServiceStatusFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__bluetoothServiceStatus))

        self.__bluetoothServiceSwitchFile = self.__bluetoothServiceFile.AddNewChildFile("switch")
        self.__bluetoothServiceSwitchFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__bluetoothServiceSwitch))

        self.__bluetoothServiceDevicesFile = self.__bluetoothServiceFile.AddNewChildFile("devices")
        self.__bluetoothServiceDevicesFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__getBluetoothDevices))

    def __bluetoothServiceStatus(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        data = {}
        data["running"] = False
        data["debug"] = False
        data["error"] = self.__systemModule.NoErrorResponse
        if self.__bluetoothManager != None:
            data["running"] = self.__bluetoothManager.IsRunning()
            data["debug"] = self.__bluetoothManager.IsDebug()
        else:
            data["error"] = {
                "set": True,
                "message": "Bluetoothmanager not defined"
            }
        return json.dumps(data)

    def __bluetoothServiceSwitch(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        
        if self.__bluetoothManager != None:
            if "running" in request.GetParameters:
                value = str(request.GetParameters["running"][0])
                if "true" == value:
                    self.__bluetoothManager.Start()
                elif "false" == value:
                    self.__bluetoothManager.Stop()
            if "debug" in request.GetParameters:
                value = str(request.GetParameters["debug"][0])
                if self.__bluetoothManager.IsDebug() and not value:
                    BluetoothManagerSetDebugMode(value)
                    if self.__bluetoothManager.IsRunning():
                        self.__bluetoothManager.Stop()
                        self.__bluetoothManager.Start()

        return self.__bluetoothServiceStatus(file, request)

    def __getBluetoothDevices(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        data = {}
        data["error"] = self.__systemModule.NoErrorResponse
        if self.__bluetoothManager != None:
            if "filter" in request.GetParameters:
                value = str(request.GetParameters["filter"][0])
                data["devices"] = self.__bluetoothManager.GetFilteredAvailableDevices(value)
            else:
                data["devices"] = self.__bluetoothManager.GetAvailableDevices()
        else:
            data["error"] = {
                "set": True,
                "message": "Bluetoothmanager not defined"
            }

        return json.dumps(data)

__bluetoothMod = BluetoothModule()