from json import JSONDecoder, JSONEncoder
import json
import os
import ssl
from ..VirtualFile import VirtualFile

#from https://pythontic.com/serialization/json/introduction
class _ConfigEncoder(JSONEncoder):
    
    def default(self, object):
        if isinstance(object, Config):
            return object.__dict__
        else:
            return json.JSONEncoder.default(self, object)
        
class _ConfigDecoder(JSONDecoder):
    def default(self, o):
        try:
            #TODO checkType
            #print("11111111111111111111111111111111111")
            #print(o)
            iterable = iter(o)
        except TypeError:
            return json.JSONEncoder.default(self, o)

        return list(iterable)
        
    
class Config:
    __configFile = "server.conf"

    def __init__(self, configFile : str,
                    standardPath : str,
                    hostAddress : str,
                    serverPort : int,
                    title : str,
                    serveableFileExtensions : tuple[str],
                    rootFile : VirtualFile,
                    tslMinimumVersion : ssl.TLSVersion,
                    debug : bool,
                    wwwFolder : str,
                    saveFolder : str,
                    sslKeyPath : str,
                    sslCertPath : str,
                 ) -> None:
        
        ######################### Standard values #########################
        self.StandardPath = standardPath
        self.HostAddress = hostAddress
        self.ServerPort = serverPort
        self.Title = title
        self.ServeableFileExtensions = serveableFileExtensions
        self.RootFile = rootFile
        self.TSLMinimumVersion = tslMinimumVersion
        self.Debug = debug

        ######################### Absolute paths #########################
        self.RunningDirectory = wwwFolder
        self.SaveFileFolder = saveFolder
        self.SSLKeyPath = sslKeyPath
        self.SSLCertPath = sslCertPath

        self.__configFile = configFile #type: str

        self.__load()
        
    def __load(self):
        #type: (str) -> Config
        
        #TODO load self.__configFile
        #print("LOAD:----------------------------------------")
        if os.path.exists(self.__configFile) and os.path.isfile(self.__configFile):
            file = open(self.__configFile, "rt")
            try:
                decoder = _ConfigDecoder()
                data = decoder.decode(file.read())
                #print(data)
            finally:
                file.close()

    def Save(self):
        #type: (str) -> None
        #TODO
        #print("SAVE:----------------------------------------")
        file = None

        try:
            if not (os.path.exists(self.__configFile)):
                file = open(self.__configFile, "xt")
            else:
                file = open(self.__configFile, "wt")

            try:
                encoder = _ConfigEncoder()
                data = encoder.encode(self)
                #print(data)
            finally:
                file.close()
        except:
            #TODO log
            pass

