from typing import Callable
from Home.Webserver.VirtualFile import METHOD_GET, TYPE_HTMLFILE, TYPE_JSONFILE, ServerRequest, VirtualFile, VirtualFileHandler
from Home.Utils.Event import Event

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

ONSAVE = IOEvent()
ONLOAD = IOEvent()
ONCLOSE = Event()
ONINIT = Event()


NOERRORRESPONSE = {
    "set": False,
    "message": None
}

def ListVirtualFiles(file, request):
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

ROOTFILE = VirtualFile(None, "root")
ROOTFILE.Bind(VirtualFileHandler(METHOD_GET, TYPE_HTMLFILE,ListVirtualFiles))

def SaveModules(saveFolder):
    ONSAVE(saveFolder)


def LoadModules(saveFolder):
    ONLOAD(saveFolder)

def CloseModules():
    ONCLOSE()

def InitModules(debug : bool):
    ONINIT(debug)

