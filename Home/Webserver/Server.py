# Python 3 server example
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
import sys
import time
from urllib.parse import parse_qs, urlparse, ParseResult
import os
from Home.Webserver.VirtualFile import ServerRequest, VirtualFile, VirtualFileHandler, METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE
import json
#import Home.Plants.PlantManager as PM
#import Home.Hardware.Sensors.Water.AlwaysActiveWaterSensor as AAWS
import Home.Hardware.BluetoothManager as BM

logger = logging.Logger(__file__)

class HybridServer(HTTPServer):
    __id = 0
    def __init__(self, server_address, RequestHandlerClass, virtualRootFile, runningDirectory = "", serviceableFileExtensions = [], standardpath = "/index.html", bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.__id = HybridServer.__id
        HybridServer.__id += 1
        self.__rootFile = virtualRootFile
        self.__serviceableFileExtensions = serviceableFileExtensions
        self.__runningDirectory = runningDirectory
        self.__standardPath = standardpath
        self.__logger = logger.getChild("HybridServer" + str(self.__id))

    @property
    def Logger(self):
        #type: () -> logging.Logger
        return self.__logger
    @property
    def RootFile(self):
        #type: () -> VirtualFile
        return self.__rootFile
    @property
    def ServiceableFileExtensions(self):
        #type: () -> list[str]
        return self.__serviceableFileExtensions
    @property
    def StandardPath(self):
        #type: () -> str
        return self.__standardPath
    @property
    def RunningDirectory(self):
        #type: () -> str
        return self.__runningDirectory

class HybridServerRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        #get get-parameters
        parsedURL = urlparse(self.path)

        uri = self.path.lstrip("/").split("?")

        relativePath = uri[0]
        getParams = None
        if len(uri) > 1:
            getParams = uri[1]

        self.path = parsedURL.path
        server = None
        if isinstance(self.server,HybridServer):
            server = self.server #type: HybridServer
            server.__class__ = HybridServer
            if relativePath == "":
                relativePath = server.RunningDirectory + "/" + server.StandardPath
            else:
                relativePath = server.RunningDirectory + "/" + relativePath

            #print(relativePath)

            if os.path.exists(relativePath) and os.path.isfile(relativePath) and relativePath.endswith(server.ServiceableFileExtensions):
                #print("Serving file: " + os.getcwd() + "/" + relativePath)
                self.path = relativePath
                if getParams != None:
                    self.path += "?" + getParams
                self.send_response(200)
                self.send_header("Content-type", TYPE_HTMLFILE.ContentType)
                self.end_headers()
                
                file = open(relativePath, 'rb')

                self.copyfile(file, self.wfile)

                #return SimpleHTTPRequestHandler.do_GET(self)
            else:

                file = server.RootFile.GetFileOrNone(self.path)
                if file != None and file.HasMethodHandler(METHOD_GET):
                    response = None #type: str | None
                    #print("Got Virtual File: " + self.path, flush=True)
                    try:
                        response = file.Excecute(METHOD_GET, ServerRequest(self.headers, parse_qs(parsedURL.query), ""))
                        #print("Got Response", flush=True)
                    except Exception as e:
                        print(sys.exc_info()[2])
                        print(e)
                        #TODO LOG

                    if response != None:
                        self.send_response(200)
                        self.send_header("Content-type", file.GetMethodHandler(METHOD_GET).Type.ContentType)
                        self.end_headers()

                        self.wfile.write(bytes(response, "utf-8"))
                    else:
                        self.SendInternalError()
                else:
                    self.SendFileNotFound()
        else:
            self.SendInternalError()
            #raise TypeError("HybridServerRequestHandler needs a HybridServer to be run on")

    def do_POST(self):
        #get get-parameters
        parsedURL = urlparse(self.path)
        #print(self.headers)
        #TODO handle multipart?
        #print(self.headers.is_multipart())

        self.path = parsedURL.path
        server = None
        if isinstance(self.server,HybridServer):
            server = self.server #type: HybridServer
            server.__class__ = HybridServer

            file = server.RootFile.GetFileOrNone(self.path)
            if file != None and file.HasMethodHandler(METHOD_POST):
                response = None #type: str | None
                #print("Got Virtual File: " + self.path, flush=True)
                try:
                    response = file.Excecute(METHOD_POST, ServerRequest(self.headers, parse_qs(parsedURL.query), self.rfile.read(int(self.headers['Content-Length']))))
                    #print("Got Response", flush=True)
                except Exception as e:
                    print(sys.exc_info()[2])
                    print(e)
                    #TODO LOG

                if response != None:
                    self.send_response(200)
                    self.send_header("Content-type", file.GetMethodHandler(METHOD_POST).Type.ContentType)
                    self.end_headers()

                    self.wfile.write(bytes(response, "utf-8"))
                else:
                    self.SendInternalError()
            else:
                self.SendFileNotFound()
        else:
            self.SendInternalError()

    def SendFileNotFound(self):
        self.send_response(404)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.path = "Error404.html"
        if os.path.exists(self.path) and os.path.isfile(self.path):
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.wfile.write(bytes("<!DOCTYPE><html><body><h1>404: FILE NOT FOUND</h1></body></html>", "utf-8"))
    
    def SendInternalError(self):
        self.send_response(500)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.path = "Error500.html"
        
        if os.path.exists(self.path) and os.path.isfile(self.path):
            return SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.wfile.write(bytes("<!DOCTYPE><html><body><h1>500: INTERNAL SERVER ERROR</h1></body></html>", "utf-8"))
    
    #TODO
    def log_message(self, format, *args):
        if isinstance(self.server,HybridServer):
            server = self.server #type: HybridServer
            server.__class__ = HybridServer
            message = format.replace("%s", "{}").format(*args)
            status = str(args[1])
            
            if status.startswith(("1", "2", "3", "4")):
                server.Logger.debug(message)
            else:
                server.Logger.critical(message)