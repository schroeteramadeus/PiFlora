from abc import ABC, abstractmethod
import json
import logging
import os
from ..Config import Config
from ...VirtualFile import METHOD_GET, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from ....Utils.VirtualLogger import VirtualLogger

#TODO instead of setup files
class ServerModule(ABC):
    __Modules = {} #type:dict[type, ServerModule]

    __modulesInited = False

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
    def OnInit(self, debug : bool, rootFile : VirtualFile) -> None:
        pass

    def __getModSaveFileFolder(saveFileFolder, mod : type):
        #type: (str, ServerModule) -> str
        return saveFileFolder + "/" + str(mod.__name__.replace(".", "_"))

    def SaveModules(config : Config):
        if ServerModule.__modulesInited:
            if not os.path.exists(config.SaveFileFolder):
                os.mkdir(config.SaveFileFolder)
            for mod in ServerModule.__Modules:
                modSaveFileFolder = ServerModule.__getModSaveFileFolder(config.SaveFileFolder, mod)
                if not os.path.exists(modSaveFileFolder):
                    os.mkdir(modSaveFileFolder)
                ServerModule.__Modules[mod].OnSave(modSaveFileFolder)

    def LoadModules(config : Config):
        if ServerModule.__modulesInited:
            for mod in ServerModule.__Modules:
                modSaveFileFolder = ServerModule.__getModSaveFileFolder(config.SaveFileFolder, mod)
                ServerModule.__Modules[mod].OnLoad(modSaveFileFolder)

    def CloseModules(config : Config):
        if ServerModule.__modulesInited:
            for mod in ServerModule.__Modules:
                ServerModule.__Modules[mod].OnClose()
            ServerModule.__modulesInited = False

    def InitModules(config : Config):
        if not ServerModule.__modulesInited:
            for mod in ServerModule.__Modules:
                ServerModule.__Modules[mod].OnInit(config.Debug, config.RootFile)
            ServerModule.__modulesInited = True

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
    def OnInit(self, debug : bool, rootFile : VirtualFile) -> None:
        if debug:
            self.__onlineHandler.setLevel(logging.DEBUG)

        self.__systemFile = rootFile.AddNewChildFile("system")
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

    def ListVirtualFiles(self, file, request):
        #type: (VirtualFile, ServerRequest) -> str

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

        html = "<!DOCTYPE html><html><head>" + head + "</head><body>" + body + "</body></html>"
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

