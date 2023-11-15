import json
import re
from typing import Type
from .InitialSetup import ServerModule, SystemModule
from ....Hardware.GPIOManager import GPIOManager, GPIOTypes
from ...VirtualFile import METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from ....Hardware.Sensors.Plant.MiFloraPlantSensor import MiFloraPlantSensor as MiFloraPlantSensor

class GPIOModule(ServerModule):
    def __init__(self) -> None:
        if GPIOModule.TryGet() == None:
            super().__init__()
            self.__gpioManager = GPIOManager
            self.__systemModule : SystemModule = None

    def OnSave(self, saveFolderPath : str) -> None:
        pass

    def OnLoad(self, saveFolderPath : str) -> None:
        pass

    def OnClose(self) -> None:
        pass

    def OnInit(self, debug : bool, rootFile : VirtualFile) -> None:
        self.__systemModule = SystemModule.Get()
        
        self.__gpioServiceFile : VirtualFile = rootFile.AddNewChildFile("gpioservice")
        self.__gpioServiceFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,self.__systemModule.ListVirtualFiles))

        self.__gpioServiceGPIOFile : VirtualFile = self.__gpioServiceFile.AddNewChildFile("gpios")
        self.__gpioServiceGPIOFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,self.__systemModule.ListVirtualFiles))

        self.__gpioServiceGPIOAvailableFile : VirtualFile = self.__gpioServiceGPIOFile.AddNewChildFile("available")
        self.__gpioServiceGPIOAvailableFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__getAvailableGPIOs))

        self.__gpioServiceGPIOAllFile : VirtualFile = self.__gpioServiceGPIOFile.AddNewChildFile("all")
        self.__gpioServiceGPIOAllFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__getAllGPIOs))

    @property
    def GPIOManager(self) -> Type[GPIOManager]:
        return self.__gpioManager

    def __getAllGPIOs(self, file : VirtualFile, request : ServerRequest) -> str:
        data = {}
        data["gpios"] = []

        gpios = []

        data["error"] = self.__systemModule.NoErrorResponse
        if self.__gpioManager != None:
            if "filter" in request.GetParameters:
                value = str(request.GetParameters["filter"][0])
                for t in GPIOTypes.GetAll():
                    if value == t.Name:
                        gpios = self.__gpioManager.GetFilteredGPIOs(t)
            else:
                gpios = self.__gpioManager.GetAllGPIOs()
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

    def __getAvailableGPIOs(self, file : VirtualFile, request : ServerRequest) -> str:
        data = {}
        data["gpios"] = []

        gpios = []

        data["error"] = self.__systemModule.NoErrorResponse
        if self.__gpioManager != None:
            if "filter" in request.GetParameters:
                value = str(request.GetParameters["filter"][0])
                for t in GPIOTypes.GetAll():
                    if value == t.Name:
                        gpios = self.__gpioManager.GetFilteredAvailableGPIOs(t)
            else:
                gpios = self.__gpioManager.GetAvailableGPIOs()
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

__gpioModule = GPIOModule()