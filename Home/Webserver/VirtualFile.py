from typing import Callable
from urllib.parse import ParseResult, parse_qs, urlparse

#TODO add input AND output file type
#TODO add header class (with method, filetypes, etc.)
#TODO use header class for bound function distinction

class _VirtualFileType:
    def __init__(self, contentType : str) -> None:
        self.__contentType = contentType

    @property
    def ContentType(self) -> str:
        return self.__contentType

    #def __eq__(self, obj):
    #    return isinstance(obj, __VirtualFileType) and obj.ContentType == self.ContentType

TYPE_HTMLFILE = _VirtualFileType("text/html")
TYPE_JSONFILE = _VirtualFileType("application/json")


class _VirtualFileMethod:
    def __init__(self, method : str) -> None:
        self.__method = method

    @property
    def Name(self) -> str:
        return self.__method

    #def __eq__(self, obj):
    #    return isinstance(obj, __VirtualFileMethod) and obj.Name == self.Name

METHOD_GET = _VirtualFileMethod("GET")
METHOD_POST = _VirtualFileMethod("POST")

class ServerRequest:
    def __init__(self, headers : dict[str,str], getParams : dict[str,list[str]], data : str) -> None:
        self.__headers : dict[str,str] = headers
        self.__getParameters : dict[str,list[str]] = getParams
        self.__data : str = data

    @property
    def Headers(self) -> dict[str,str]:
        return self.__headers

    @property
    def GetParameters(self) -> dict[str,list[str]]:
        return self.__getParameters

    @property
    def Data(self) -> str:
        return self.__data

class VirtualFileHandler:

    def __init__(self, method : _VirtualFileMethod, type : _VirtualFileType, func : Callable[['VirtualFile', ParseResult], str]) -> None:
        self.__method = method
        self.__func = func
        self.__type = type

    def excecute(self, file : 'VirtualFile', data : ServerRequest) -> str:
        return self.__func(file, data)
    
    @property
    def Method(self) -> _VirtualFileMethod:
        return self.__method

    @property
    def Func(self) -> Callable[['VirtualFile', ParseResult], str]:
        return self.__func
    
    @property
    def Type(self) -> _VirtualFileType:
        return self.__type

class VirtualFile:
    def __init__(self,parent : 'VirtualFile', name : str) -> None:
        if not "/" in name:
            self.__name : str = name.lower()
            self.__parent : VirtualFile = parent
            self.__childs : dict[str, VirtualFile] = {}
            self.__fileHandlers : dict[_VirtualFileMethod, VirtualFileHandler] = {}
            
            if self.__parent != None:
                if not self.__name in self.__parent.__childs:
                    self.__parent.__childs[self.__name] = self
                else:
                    raise ValueError(self.__parent.FullPath + "/" + self.__name + " already exists")
            #else:
            #    pass
                #pretend its a new file system
        else:
            raise ValueError("name can not contain \"/\"")

    def AddNewChildFile(self, name : str) -> 'VirtualFile':
        if not self.FileExists(name):
            return VirtualFile(self, name)
        else:
            raise ValueError(self.FullPath + "/" + name + " already exists")

    def FileExists(self, path : str) -> bool:
        try:
            self.GetFile(path)
        except(ValueError):
            return False

        return True

    def GetFile(self, path : str) -> 'VirtualFile':
        path = path.replace("\\", "/").rstrip("/").lower()
        names = path.split("/")

        if path.startswith("/"):
            #go to root file
            if self.Parent != None:
                return self.Parent.GetFile(path)
            else:
                if len(names) > 2:
                    if names[1] == self.Name:
                        return self.GetFile("/".join(names[2:]))
                    else:
                        raise ValueError("File " + path + " does not exist, root was: /" + self.Name)
                else:
                    return self
                # if self.Name == names[1]: #starts with ""
                #     if len(names) > 3:
                #         if names[2] in self.__childs:
                #             return self.__childs[names[2]].GetFile("/".join(names[3:]))
                #         else:
                #             raise ValueError("File " + self.FullPath + path + " does not exist")
                #     elif len(names) > 2:
                #         if names[2] in self.__childs:
                #             return self.__childs[names[2]]
                #         else:
                #             raise ValueError("File " + self.FullPath + path + " does not exist")
                #     else:
                #         return self

        else:
            if len(names) > 0 and names[0] != "":
                if names[0] in self.__childs:
                    if len(names) > 1:
                        return self.__childs[names[0]].GetFile("/".join(names[1:]))
                    else:
                        return self.__childs[names[0]]
                else:
                    raise ValueError("File " + self.FullPath + "/" + path + " does not exist")
            else:
                raise ValueError("Path not vaid")     

    def GetFileOrNone(self, path : str) -> 'VirtualFile' | None:
        try:
            return self.GetFile(path)
        except(ValueError):
            #TODO log error
            return None

    def GetAllFiles(self) -> list['VirtualFile']:
        childs = []
        for name in self.__childs:
            childs.append(self.__childs[name])

        return childs

    @property
    def FullPath(self) -> str:
        path = self.Name
        parent = self.Parent
        while parent != None:
            path = parent.Name + "/" + path
            parent = parent.Parent
        return "/" + path

    @property
    def Childs(self) -> dict[str, 'VirtualFile']:
        return self.__childs
    @property
    def Name(self) -> str:
        return self.__name
    @property
    def Parent(self) -> 'VirtualFile' | None:
        return self.__parent

    def Excecute(self, method : _VirtualFileMethod, data : ServerRequest) -> str:
        if self.HasMethodHandler(method):
            return self.__fileHandlers[method].excecute(self,data)
        else:
            raise AttributeError("No such method: " + method.Name + " in " + self.FullPath)

    def HasMethodHandler(self, method : _VirtualFileMethod) -> str:
        if method in self.__fileHandlers:
            return True
        else:
            return False

    def GetMethodHandler(self, method : _VirtualFileMethod) -> VirtualFileHandler:
        if self.HasMethodHandler(method):
            return self.__fileHandlers[method]
        else:
            raise AttributeError("No such method: " + method.Name + " in " + self.FullPath)

    def Bind(self, handler : VirtualFileHandler) -> None:
        if not self.HasMethodHandler(handler.Method):
            self.__fileHandlers[handler.Method] = handler
        else:
            raise ValueError("Method " + handler.Method.Name + " already used for file " + self.FullPath)
    
    def Unbind(self, handler : VirtualFileHandler) -> None:
        if self.HasMethodHandler(handler.Method):
            self.__fileHandlers.pop(handler.Method)
        else:
            raise ValueError("Method " + handler.Method.Name + " not used for file " + self.FullPath)
