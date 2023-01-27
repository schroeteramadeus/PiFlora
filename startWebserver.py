import logging
import os
import ssl
import sys
from ConsoleFilter import ConsoleFilter
from Home.Webserver.Server import HybridServer, HybridServerRequestHandler

from Home.Utils.ArgumentParser import *
from serverSetup import Save, Load, HOSTNAME, ROOTFILE, SERVERPORT, SERVEABLEFILEEXTENSIONS, BLUETOOTHMANAGER, PLANTMANAGER, STANDARDPATH

def main(runningDirPath, saveFilePath, sslKeyPath, sslCertPath):

    print("Loading data...")
    Load(saveFilePath)
    print("Server starting on " + dir)
    webServer = HybridServer((HOSTNAME, SERVERPORT), RequestHandlerClass=HybridServerRequestHandler,virtualRootFile=ROOTFILE, serviceableFileExtensions=SERVEABLEFILEEXTENSIONS, standardpath=STANDARDPATH, runningDirectory=runningDirPath)

    print("Server starting on " + dir)

    webServer.socket = ssl.wrap_socket(webServer.socket, 
        keyfile=sslKeyPath,#"config/ssl/key.pem", 
        certfile=sslCertPath,#"config/ssl/cert.pem", 
        server_side=True)

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
            Save(saveFilePath)
        webServer.server_close()
        print("Server stopped.")


if __name__ == "__main__":   

    runningDirPath = "www"
    saveFilePath = "config/save.conf"
    sslKeyPath = "config/ssl/key.pem"
    sslCertPath = "config/ssl/cert.pem"

    argParser = ArgumentParser()
    argParser.addArgument(Argument("www", str))
    argParser.addArgument(Argument("save", str))
    argParser.addArgument(Argument("sslKey", str))
    argParser.addArgument(Argument("sslCert", str))

    argParser.parseArguments(sys.argv)

    www = str(argParser.getParsedValue("www")).rstrip("/")
    save = str(argParser.getParsedValue("save")).rstrip("/")
    sslKey = str(argParser.getParsedValue("sslKey")).rstrip("/")
    sslCert = str(argParser.getParsedValue("sslCert")).rstrip("/")

    if www != None and www != "":
        runningDirPath = www
    if save != None and save != "":
        saveFilePath = save
    if sslKey != None and sslKey != "":
        sslKeyPath = sslKey
    if sslCert != None and sslCert != "":
        sslCertPath = sslCert

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.addFilter(ConsoleFilter())

    root.addHandler(handler)
    main(runningDirPath, saveFilePath, sslKeyPath, sslCertPath)