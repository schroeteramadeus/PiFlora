import os
from Home.Webserver.Server import HybridServer, ServerRequestHandler

from serverSetup import Save, Load, HOSTNAME, ROOTFILE, SERVERPORT, SERVEABLEFILEEXTENSIONS, BLUETOOTHMANAGER, PLANTMANAGER, STANDARDPATH

def main():
    dir = input("Running directory (Press enter, to use the current working directory): ")
    if dir == "":
        dir = os.getcwd()
    else:
        os.chdir(dir)

    saveFile = input("Saving file (Press enter, to use " + dir + "\\save.conf): ")
    if saveFile == "":
        saveFile = os.getcwd() + "\\save.conf"
    elif not os.path.isfile(saveFile):
        raise AttributeError(saveFile + " does not exist or is not a file.")

    print("Loading data...")
    Load(saveFile)
    print("Server starting on " + dir)
    webServer = HybridServer((HOSTNAME, SERVERPORT), RequestHandlerClass=ServerRequestHandler,virtualRootFile=ROOTFILE, serviceableFileExtensions=SERVEABLEFILEEXTENSIONS, standardpath=STANDARDPATH)


    #activate SSL (HTTPS)

    #webServer.socket = ssl.wrap_socket (webServer.socket, 
    #    keyfile="path/to/key.pem", 
    #    certfile='path/to/cert.pem', server_side=True)

    print("Server started http://%s:%s" % (HOSTNAME, SERVERPORT))

    #TODO set up saving thread
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        if PLANTMANAGER != None and PLANTMANAGER.IsRunning:
            PLANTMANAGER.Stop()
        if BLUETOOTHMANAGER != None and BLUETOOTHMANAGER.IsRunning():
            BLUETOOTHMANAGER.Stop()
        if not PLANTMANAGER.IsDebug:
            Save(saveFile)
        webServer.server_close()
        print("Server stopped.")


if __name__ == "__main__":   
    main()