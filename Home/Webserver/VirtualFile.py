from typing import Callable
from urllib.parse import ParseResult, parse_qs, urlparse

#TODO add input AND output file type
#TODO add header class (with method, filetypes, etc.)
#TODO use header class for bound function distinction

class _VirtualFileType:
    def __init__(self, contentType) -> None:
        self.__contentType = contentType

    @property
    def ContentType(self):
        return self.__contentType

    #def __eq__(self, obj):
    #    return isinstance(obj, __VirtualFileType) and obj.ContentType == self.ContentType

TYPE_HTMLFILE = _VirtualFileType("text/html")
TYPE_JSONFILE = _VirtualFileType("application/json")


class _VirtualFileMethod:
    def __init__(self, method) -> None:
        #type: (str) -> None
        self.__method = method

    @property
    def Name(self):
        #type: () -> str
        return self.__method

    #def __eq__(self, obj):
    #    return isinstance(obj, __VirtualFileMethod) and obj.Name == self.Name

METHOD_GET = _VirtualFileMethod("GET")
METHOD_POST = _VirtualFileMethod("POST")

class ServerRequest:
    def __init__(self, headers, getParams, data) -> None:
        #type: (dict[str,str], dict[str,list[str]], str) -> None
        self.__headers = headers #type: dict[str,str]
        self.__getParameters = getParams #type: dict[str,list[str]]
        self.__data = data #type:str

    @property
    def Headers(self):
        #type: () -> dict[str,str]
        return self.__headers

    @property
    def GetParameters(self):
        #type: () -> dict[str,list[str]]
        return self.__getParameters

    @property
    def Data(self):
        #type: () -> str
        return self.__data

class VirtualFileHandler:

    def __init__(self, method, type, func) -> None:
        #type: (_VirtualFileMethod, _VirtualFileType, Callable[[VirtualFile, ParseResult], str]) -> None
        self.__method = method
        self.__func = func
        self.__type = type

    def excecute(self, file, data):
        #type: (VirtualFile, ServerRequest) -> str
        return self.__func(file, data)
    
    @property
    def Method(self):
        return self.__method

    @property
    def Func(self):
        return self.__func
    
    @property
    def Type(self):
        return self.__type

class VirtualFile:
    def __init__(self,parent, name) -> None:
        #type: (VirtualFile, str) -> None
        if not "/" in name:
            self.__name = name.lower()
            self.__parent = parent
            self.__childs = {} #type: dict[str, VirtualFile]
            self.__fileHandlers = {} #type: dict[_VirtualFileMethod, VirtualFileHandler]
            
            if self.__parent != None:
                if not self.__parent.FileExists(self.__name):
                    self.__parent.__childs[self.__name] = self
                else:
                    raise ValueError(self.__parent.FullPath + "/" + self.__name + " already exists")
            #else:
            #    pass
                #pretend its a new file system
        else:
            raise ValueError("name can not contain \"/\"")

    def AddNewChildFile(self, name):
        #type: (str) -> VirtualFile
        if not self.FileExists(name):
            return VirtualFile(self, name)
        else:
            raise ValueError(self.FullPath + "/" + name + " already exists")

    def FileExists(self, path):
        #type: (str) -> bool       
        try:
            self.GetFile(path)
        except(ValueError):
            return False

        return True

    def GetFile(self, path):
        #type: (str) -> VirtualFile
        path = path.rstrip("/").lower()
        names = path.split("/")

        if path.startswith("/"):
            #go to root file
            if self.Parent != None:
                return self.Parent.GetFile(path)
            else:
                if self.Name == names[1]: #starts with ""
                    if len(names) > 3:
                        if names[2] in self.__childs:
                            return self.__childs[names[2]].GetFile("/".join(names[3:]))
                        else:
                            raise ValueError("File " + self.FullPath + path + " does not exist")
                    elif len(names) > 2:
                        if names[2] in self.__childs:
                            return self.__childs[names[2]]
                        else:
                            raise ValueError("File " + self.FullPath + path + " does not exist")
                    else:
                        return self

        else:
            if names[0] != "":
                if names[0] in self.__childs:
                    if len(names) > 1:
                        return self.__childs[names[0]].GetFile("/".join(names[1:]))
                    else:
                        return self.__childs[names[0]]
                else:
                    raise ValueError("File " + self.FullPath + path + " does not exist")
            else:
                raise ValueError("Path not vaid")     

    def GetFileOrNone(self, path):
        #type: (str) -> VirtualFile | None
        try:
            return self.GetFile(path)
        except(ValueError):
            return None

    def GetAllFiles(self):
        #type: () -> list[VirtualFile]
        childs = []
        for name in self.__childs:
            childs.append(self.__childs[name])

        return childs

    @property
    def FullPath(self):
        #type: () -> str    
        path = self.Name
        parent = self.Parent
        while parent != None:
            path = parent.Name + "/" + path
            parent = parent.Parent
        return "/" + path

    @property
    def Childs(self):
        #type: () -> dict[str, VirtualFile]
        return self.__childs
    @property
    def Name(self):
        #type: () -> str
        return self.__name
    @property
    def Parent(self):
        #type: () -> VirtualFile | None
        return self.__parent

    def Excecute(self, method, data):
        #type: (_VirtualFileMethod, ServerRequest) -> str
        if self.HasMethodHandler(method):
            return self.__fileHandlers[method].excecute(self,data)
        else:
            raise AttributeError("No such method: " + method.Name + " in " + self.FullPath)

    def HasMethodHandler(self, method):
        #type: (_VirtualFileMethod) -> str
        if method in self.__fileHandlers:
            return True
        else:
            return False

    def GetMethodHandler(self, method):
        #type: (_VirtualFileMethod) -> VirtualFileHandler
        if self.HasMethodHandler(method):
            return self.__fileHandlers[method]
        else:
            raise AttributeError("No such method: " + method.Name + " in " + self.FullPath)

    def Bind(self, handler) -> None:
        #type: (VirtualFileHandler) -> None
        if not self.HasMethodHandler(handler.Method):
            self.__fileHandlers[handler.Method] = handler
        else:
            raise ValueError("Method " + handler.Method.Name + " already used for file " + self.FullPath)
    
    def Unbind(self, handler) -> None:
        #type: (VirtualFileHandler) -> None
        if self.HasMethodHandler(handler.Method):
            self.__fileHandlers.pop(handler.Method)
        else:
            raise ValueError("Method " + handler.Method.Name + " not used for file " + self.FullPath)
