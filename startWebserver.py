import logging
import os
import ssl
import sys
from ConsoleFilter import ConsoleFilter
from Home.Webserver.Server import HybridServer, HybridServerRequestHandler
from Home.Utils.ArgumentParser import Argument, ArgumentParser 
import socket
from serverSetup import Save, Load, HOSTADDRESS, ROOTFILE, SERVERPORT, SERVEABLEFILEEXTENSIONS, BLUETOOTHMANAGER, PLANTMANAGER, STANDARDPATH

def main(runningDirPath : str, saveFilePath : str, sslKeyPath : str, sslCertPath : str):

    print("Loading data...")
    Load(saveFilePath)
    print("Server starting on " + runningDirPath)
    webServer = HybridServer((HOSTADDRESS, SERVERPORT), RequestHandlerClass=HybridServerRequestHandler,virtualRootFile=ROOTFILE, serviceableFileExtensions=SERVEABLEFILEEXTENSIONS, standardpath=STANDARDPATH, runningDirectory=runningDirPath)

    print("Activating TLS 1.3")
    try:
        pass
        #context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #print(ssl.HAS_TLSv1_3)
        #context.minimum_version = ssl.TLSVersion.TLSv1_3
        #TODO password
        #context.load_cert_chain(certfile=sslCertPath,keyfile=sslKeyPath)

        #webServer.socket = context.wrap_socket(webServer.socket, server_side=True)
    except Exception as e:
        print("Could not activate TLS")
        i = input("Do you want to continue without TLS? (y/n):").lower()
        while i != "y":
            if i == "n":
                raise e
            i = input("Do you want to continue without TLS? (y/n):").lower()

    hostname = socket.gethostbyaddr(HOSTADDRESS)
    print("Server started on:")
    print("\thttps://%s:%s" % (hostname[0], SERVERPORT))
    for name in hostname[1]:
        print("\thttps://%s:%s" % (name, SERVERPORT))
    for ip in hostname[2]:
        print("\thttps://%s:%s" % (ip, SERVERPORT))
        if ip == "127.0.0.1":
            print("\thttps://%s:%s" % ("localhost", SERVERPORT))

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

    wd = os.getcwd()

    runningDirPath = wd + "/www"
    saveFilePath = wd + "/config/save.conf"
    sslKeyPath = wd + "/config/ssl/cert.key"
    sslCertPath = wd + "/config/ssl/cert.csr"

    argParser = ArgumentParser()
    argParser.addArgument(Argument("www", str))
    argParser.addArgument(Argument("save", str))
    argParser.addArgument(Argument("sslKey", str))
    argParser.addArgument(Argument("sslCert", str))

    argParser.parseArguments(sys.argv[1:])

    www = argParser.getParsedValue("www")
    save = argParser.getParsedValue("save")
    sslKey = argParser.getParsedValue("sslKey")
    sslCert = argParser.getParsedValue("sslCert")

    if www != None:
        runningDirPath = str(www).rstrip("/")
    if save != None:
        saveFilePath = str(save).rstrip("/")
    if sslKey != None:
        sslKeyPath = str(sslKey).rstrip("/")
    if sslCert != None:
        sslCertPath = str(sslCert).rstrip("/")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.addFilter(ConsoleFilter())

    root.addHandler(handler)
    main(runningDirPath, saveFilePath, sslKeyPath, sslCertPath)