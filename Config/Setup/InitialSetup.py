from abc import ABC, abstractmethod
import json
import logging
import re
import threading
import time
from typing import Callable
from Home.Webserver.VirtualFile import METHOD_GET, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from Home.Utils.Event import Event


class VirtualLogger(logging.Handler):

    def __init__(self, maximumRecords:int = 1000, level: int = 0) -> None:
        super().__init__(level)
        self.__maximumRecords = maximumRecords #type: int
        self.__records = [] #type: list[logging.LogRecord]
        self.__recordsLock = threading.Lock() #type : threading.Lock

    def emit(self, record):
        with self.__recordsLock:
            if len(self.__records) >= self.__maximumRecords:
                self.__records.pop()
            self.__records.append(record)

    def Fetch(self, minimumLevel: int = 0, filter:str = "") -> list[dict[str,str | int]]:
        logs = []
        expression = re.compile(filter)

        with self.__recordsLock:
            for record in self.__records:
                data = {}
                data["time"] = record.asctime
                data["message"] = record.message
                data["level"] = record.levelname
                data["logger"] = record.name
                data["file"] = record.filename
                data["line"] = record.lineno
                if record.levelno >= minimumLevel:
                    if expression.match(data["message"]) or expression.match(data["level"]) or expression.match(data["file"]):
                        logs.append(data)
        return logs

    @property
    def MaximumRecords(self, value):
        #type: (int) -> None
        self.__maximumRecords = value

#TODO own directory for each module
class IOEvent(Event):
    def __iadd__(self, handler):
        #type: (Callable[[str], None]) -> None
        self._eventhandlers.append(handler)
        return self
    def __isub__(self, handler):
        #type: (Callable[[str], None]) -> None
        self._eventhandlers.remove(handler)
        return self

    def __call__(self, saveFolder : str):
        for eventhandler in self._eventhandlers:
            eventhandler(saveFolder)


#TODO instead of setup files
class ServerModule(ABC):
    __Modules = {} #type:dict[type, ServerModule]

    #NOTE: DO NOT LOAD DEPENDENCIES (other modules), instead use oninit()
    def __init__(self) -> None:
        if self.__class__ not in ServerModule.__Modules:
            ServerModule.__Modules[self.__class__] = self
        #else:
        #    raise IndexError("Module " + self.__class__ + " already exists")

    def TryGetModule(t : type):
        if t in ServerModule.__Modules:
            return ServerModule.__Modules[t]
        else:
            return None

    def GetModule(t : type):
        module = ServerModule.TryGetModule(t)
        if module == None:
            raise KeyError("Could not load " + t.__name__)
        return module
    
    @classmethod
    def Get(cls):
        return ServerModule.GetModule(cls)
    @classmethod
    def TryGet(cls):
        return ServerModule.TryGetModule(cls)

    @abstractmethod
    def OnSave(self, saveFolderPath : str) -> None:
        pass
    @abstractmethod
    def OnLoad(self, saveFolderPath : str) -> None:
        pass
    @abstractmethod
    def OnClose(self) -> None:
        pass
    #for loading dependencies of modules
    @abstractmethod
    def OnInit(self, debug : bool) -> None:
        pass

    def SaveModules(saveFolder):
        for mod in ServerModule.__Modules:
            ServerModule.__Modules[mod].OnSave(saveFolder)

    def LoadModules(saveFolder):
        for mod in ServerModule.__Modules:
            ServerModule.__Modules[mod].OnLoad(saveFolder)

    #TODO check if already inited or closed
    def CloseModules():
        for mod in ServerModule.__Modules:
            ServerModule.__Modules[mod].OnClose()

    def InitModules(debug : bool):
        for mod in ServerModule.__Modules:
            ServerModule.__Modules[mod].OnInit(debug)

class SystemModule(ServerModule):
    def __init__(self) -> None:
        super().__init__()
        #region setup logger
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s, %(filename)s:%(lineno)s")

        self.__onlineHandler = VirtualLogger()
        #TODO set to info
        self.__onlineHandler.setLevel(logging.DEBUG)
        self.__onlineHandler.setFormatter(formatter)

        self.__fileHandler = logging.FileHandler("server.log")
        #TODO get file from config?
        self.__fileHandler.setLevel(logging.DEBUG)
        self.__fileHandler.setFormatter(formatter)

        root.addHandler(self.__onlineHandler)
        root.addHandler(self.__fileHandler)
        #endregion setup logger
        
        self.__rootFile = VirtualFile(None, "root")
        self.__rootFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,self.ListVirtualFiles))

    def OnSave(self, saveFolderPath : str) -> None:
        pass
    def OnLoad(self, saveFolderPath : str) -> None:
        pass
    def OnClose(self) -> None:
        pass
    def OnInit(self, debug : bool) -> None:
        if debug:
            self.__onlineHandler.setLevel(logging.DEBUG)

        self.__systemFile = self.RootFile.AddNewChildFile("system")
        self.__systemFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,self.ListVirtualFiles))

        self.__logFile = VirtualFile(self.__systemFile, "logs")
        self.__logFile.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__getLogs))

        self.__logSwitch = VirtualFile(self.__logFile, "switch")
        self.__logSwitch.Bind(VirtualFileHandler(METHOD_GET, TYPE_JSONFILE,self.__setLogger))

    @property
    def NoErrorResponse(self) -> dict[str]:
        return {
        "set": False,
        "message": None
        }
        
    @property
    def RootFile(self):
        return self.__rootFile

    def ListVirtualFiles(self, file, request):
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

    def __getLogs(self,file, request):
        #type: (VirtualFile, ServerRequest) -> str
        data = {}
        data["error"] = self.NoErrorResponse

        filter = "_*"
        level = logging.DEBUG #type: logging._Level

        if "filter" in request.GetParameters:
            filter = str(request.GetParameters["filter"][0])
        if "level" in request.GetParameters:
            levelText = str(request.GetParameters["level"][0])
            try:
                level = getattr(logging, levelText.upper())
            except Exception as e:
                level = logging.DEBUG
                data["error"] = {
                    "set": True,
                    "message": "Level " + levelText + " not known, returning all logs for level DEBUG instead"
                }

            # if level == "debug" or level == "all":
            #     level = logging.DEBUG
            # elif level == "info" or level == "information" or level == "":
            #     level = logging.INFO
            # elif level == "info" or level == "information" or level == "":
            #     level = logging.WARNING
            # elif level == "warn" or level == "warning":
            #     level = logging.ERROR

        data["logs"] = self.__onlineHandler.Fetch(minimumLevel=level, filter=filter)

        return json.dumps(data)

    def __setLogger(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str
        data = {}
        data["error"] = self.NoErrorResponse

        if "level" in request.GetParameters:
            level = str(request.GetParameters["level"][0])
            self.__onlineHandler.setLevel(level)

        if "count" in request.GetParameters:
            count = str(request.GetParameters["count"][0])
            if count > 0:
                self.__onlineHandler.MaximumRecords = count
            else:
                data["error"] = {
                    "set": True,
                    "message": "Count needs to be > 0"
                }

        return json.dumps(data)


__systemMod = SystemModule()

