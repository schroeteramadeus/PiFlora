# Python 3 server example
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging
import sys
import time
import traceback
from urllib.parse import parse_qs, urlparse, ParseResult
import os
from .VirtualFile import ServerRequest, VirtualFile, _VirtualFileMethod, VirtualFileHandler, METHOD_GET, METHOD_POST, TYPE_HTMLFILE, TYPE_JSONFILE

logger = logging.Logger(__name__)

class HybridServer(HTTPServer):
    __id = 0
    def __init__(self, server_address, RequestHandlerClass, virtualRootFile, runningDirectory = "", serviceableFileExtensions = [], standardpath = "/index.html", bind_and_activate: bool = ...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.__id = HybridServer.__id
        HybridServer.__id += 1
        self.__rootFile = virtualRootFile
        self.__serviceableFileExtensions = tuple(serviceableFileExtensions)
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

    def __init__(self, request, client_address, server, *, directory: str | None = None) -> None:
        super().__init__(request, client_address, server, directory=directory)
        #so that guess_type() works correctly
        self.extensions_map[".js"] = "text/javascript"

    def do_GET(self):
        #get get-parameters
        parsedURL = urlparse(self.path)
        self.path = parsedURL.path
        if isinstance(self.server,HybridServer):
            absoluteSystemPath = HybridServerRequestHandler.__getAbsoluteSystemPath(self.server.RunningDirectory, self.path, self.server.StandardPath)
            if os.path.exists(absoluteSystemPath) and os.path.isfile(absoluteSystemPath) and absoluteSystemPath.endswith(self.server.ServiceableFileExtensions):
                self.path = absoluteSystemPath
                HybridServerRequestHandler.ServeStaticFile(self, 200)
            else:
                #print(self.server.RootFile.GetFileOrNone(self.path))
                HybridServerRequestHandler.ServeVirtualFile(handler=self, virtualFile=self.server.RootFile.GetFileOrNone(self.path), method=METHOD_GET, request=ServerRequest(self.headers, parse_qs(parsedURL.query), ""))
        else:
            self.SendInternalError(self)
            #raise TypeError("HybridServerRequestHandler needs a HybridServer to be run on")

    def do_POST(self):
        #get get-parameters
        parsedURL = urlparse(self.path)
        #print(self.headers)
        #TODO handle multipart?
        #print(self.headers.is_multipart())

        self.path = parsedURL.path
        if isinstance(self.server,HybridServer):
            HybridServerRequestHandler.ServeVirtualFile(handler=self, virtualFile=self.server.RootFile.GetFileOrNone(self.path), method=METHOD_POST, request=ServerRequest(self.headers, parse_qs(parsedURL.query), self.rfile.read(int(self.headers['Content-Length']))))
        else:
            self.SendInternalError(self)

    def SendFileNotFound(handler, virtual=False):
        #type: (HybridServerRequestHandler, bool) -> None
        handler.path = "Error404.html"
        if not virtual and os.path.exists(handler.path) and os.path.isfile(handler.path):
            HybridServerRequestHandler.ServeStaticFile(handler, 404)
        else:
            response = bytes("<!DOCTYPE><html><body><h1>404: FILE NOT FOUND</h1></body></html>", "utf-8")
            handler.send_response(404)
            handler.send_header("Content-type", "text/html")
            handler.send_header("Content-Length", str(len(response)))
            handler.send_header("Last-Modified", time.time())
            handler.end_headers()
            handler.wfile.write(response)
    
    def SendInternalError(handler, virtual=False):
        #type: (HybridServerRequestHandler, bool) -> None
        handler.path = "Error500.html"
        
        if not virtual and os.path.exists(handler.path) and os.path.isfile(handler.path):
            try:
                HybridServerRequestHandler.ServeStaticFile(handler, 500)
            except RecursionError:
                logger = handler.server.Logger #type: logging.Logger
                logger.warning("Can not send internal server error static file")
                HybridServerRequestHandler.SendFileNotFound(handler, True)
        else:
            response = bytes("<!DOCTYPE><html><body><h1>500: INTERNAL SERVER ERROR</h1></body></html>", "utf-8")
            handler.send_response(500)
            handler.send_header("Content-type", "text/html")
            handler.send_header("Content-Length", str(len(response)))
            handler.send_header("Last-Modified", time.time())
            handler.end_headers()
            handler.wfile.write(response)
    
    def ServeStaticFile(handler, status):
        #type: (HybridServerRequestHandler, int) -> None
        try:
            file = open(handler.path, 'rb')
            try:
                fs = os.fstat(file.fileno())
                handler.send_response(status)
                handler.send_header("Content-type", handler.guess_type(handler.path))
                handler.send_header("Content-Length", str(fs[6]))
                handler.send_header("Last-Modified", handler.date_time_string(fs.st_mtime))
                handler.end_headers()
                handler.copyfile(file, handler.wfile)
            except:
                if str(status).startswith(5):
                    handler.SendInternalError(handler)
                else:
                    raise RecursionError("Can not send internal server error static file")
            finally:
                file.close()
        except not RecursionError:
            if not str(status).startswith(5):
                handler.SendInternalError(handler)
            else:
                raise RecursionError("Can not send internal server error static file")
                       
    def ServeVirtualFile(handler, virtualFile, method, request):
        #type: (HybridServerRequestHandler, VirtualFile, _VirtualFileMethod, ServerRequest) -> None
        if virtualFile != None and virtualFile.HasMethodHandler(method):
            response = None #type: str | None
            #print("Got Virtual File: " + self.path, flush=True)
            try:
                response = bytes(virtualFile.Excecute(method, request), "utf-8")
                #print("Got Response", flush=True)
            except Exception as e:
                traceback.print_exc()
                #print(sys.exc_info()[2])
                print(e)
                #TODO LOG

            if response != None:
                handler.send_response(200)
                handler.send_header("Content-type", virtualFile.GetMethodHandler(method).Type.ContentType)
                handler.send_header("Content-Length", len(response))
                handler.send_header("Last-Modified", time.time())
                handler.end_headers()

                handler.wfile.write(response)
            else:
                handler.SendInternalError(handler)
        else:
            handler.SendFileNotFound(handler)
       
    def __getAbsoluteSystemPath(runningDir : str, relativePath : str, standardPath : str):
        absolutePath = runningDir + "/" + relativePath.replace("../", "")
        if os.path.isdir(absolutePath):
            absolutePath += "/" + standardPath

        return absolutePath

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