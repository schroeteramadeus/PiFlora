import json
import os
import ssl
from ..VirtualFile import VirtualFile

#from https://pythontic.com/serialization/json/introduction
class _ConfigEncoder:
    SERIALIZATIONTYPE = "SERIALIZATIONTYPE_DO_NOT_CHANGE"
    def encode(obj):
        tName = obj.__class__.__name__
        if isinstance(obj, Config):
            obj = obj.__dict__
            obj["RootFile"] = obj["RootFile"].Name
            obj["TSLMinimumVersion"] = str(obj["TSLMinimumVersion"])
            obj.pop("_Config__configFile")
            obj.pop("Debug")
            obj[_ConfigEncoder.SERIALIZATIONTYPE] = tName
        return json.dumps(obj, indent=4)
        
class _ConfigDecoder:
    def decode(jsonData):
        try:
            jsonData = json.loads(jsonData) #type: dict[str]
            if _ConfigEncoder.SERIALIZATIONTYPE in jsonData:
                if jsonData[_ConfigEncoder.SERIALIZATIONTYPE] == Config.__name__:
                    jsonData["RootFile"] = VirtualFile(None, jsonData["RootFile"])
                    for v in ssl.TLSVersion:
                        if str(v) == jsonData["TSLMinimumVersion"]:
                            jsonData["TSLMinimumVersion"] = v
                            break
                    else:
                        raise ValueError("TSLVersion " + jsonData["TSLMinimumVersion"] + " not supported")
                    jsonData.pop(_ConfigEncoder.SERIALIZATIONTYPE)
                    return jsonData
            else:
                return {}
        except:
            return {}

        
    
class Config:
    def __init__(self, configFile : str,
                    standardPath : str,
                    hostAddress : str,
                    serverPort : int,
                    title : str,
                    serveableFileExtensions : tuple[str],
                    rootFileName : str,
                    tslMinimumVersion : ssl.TLSVersion,
                    debug : bool,
                    wwwFolder : str,
                    saveFolder : str,
                    logFilePath : str,
                    sslPath : str,
                    sslKeyFile : str,
                    sslCertFile : str,
                 ) -> None:
        
        ######################### Standard values #########################
        self.StandardPath = standardPath
        self.HostAddress = hostAddress
        self.ServerPort = serverPort
        self.Title = title
        self.ServeableFileExtensions = serveableFileExtensions
        self.RootFile = None
        self.TSLMinimumVersion = tslMinimumVersion
        self.Debug = debug

        ######################### Absolute paths #########################
        self.RunningDirectory = wwwFolder
        self.SaveFileFolder = saveFolder
        self.LogFilePath = logFilePath
        self.SSLPath = sslPath
        self.SSLKeyFile = sslKeyFile
        self.SSLCertFile = sslCertFile

        self.__configFile = configFile #type: str

        self.__load()
        
        if self.RootFile == None:
            self.RootFile = VirtualFile(None, rootFileName)

    @property
    def SSLKeyPath(self):
        return self.SSLPath + "/" + self.SSLKeyFile
    
    @property
    def SSLCertPath(self):
        return self.SSLPath + "/" + self.SSLCertFile
        
    def __load(self):
        #type: (str) -> Config
        
        if os.path.exists(self.__configFile) and os.path.isfile(self.__configFile):
            file = open(self.__configFile, "rt")
            try:
                data = file.read()
                if data != "":
                    data = _ConfigDecoder.decode(data)
                if data != None:
                    print("Loading config...")
                    for key in data:
                        if key in self.__dict__ and self.__dict__[key] != data[key]:
                            if key != "RootFile":
                                print(key + ": " + str(data[key]))
                                self.__dict__[key] = data[key]
                    print("Config up to date")
            finally:
                file.close()

    def Save(self):
        #type: (str) -> None
        file = None

        if not (os.path.exists(self.__configFile)):
            file = open(self.__configFile, "xt")
        else:
            file = open(self.__configFile, "wt")

        try:
            data = _ConfigEncoder.encode(self)
            file.write(data)
        finally:
            file.close()

