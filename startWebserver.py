import logging
import traceback
from Home.Utils.ArgumentParser import Argument, ArgumentParser, Switch 
from Home.Webserver.Config.Config import Config
import os
import ssl
import sys
from typing import Callable
#from ConsoleFilter import ConsoleFilter
import socket
from VueCompiler import VueCompiler

#TODO use GraphQL for get/post requests
if __name__ == "__main__":
    
    compiling = False
    vueFolder = os.getcwd() + "/vue"
    configFolder = os.getcwd() + "/config"
    if not os.path.exists(configFolder):
        os.mkdir(configFolder)

    #this initial config will be overridden by the config file (if existing)
    config = Config(configFile = configFolder + "/server.conf",
                    standardPath = "index.html",
                    hostAddress = "127.0.0.1",
                    serverPort = 8080,
                    title = "Home",
                    serveableFileExtensions = [".html", ".htm", ".ico", ".png", ".svg", ".jpeg", ".jpg", ".gif", ".tiff", ".ttf", ".woff2", ".js", ".ts", ".css", ".min", ".json", ".map"],
                    rootFileName = "root",
                    tslMinimumVersion = ssl.TLSVersion.TLSv1_3,
                    debug = False,
                    compileFolder = vueFolder,
                    wwwFolder = vueFolder + "/dist",
                    saveFolder = configFolder + "/save",
                    logFilePath = configFolder + "/server.log",
                    sslPath = configFolder + "/ssl",
                    sslKeyFile = "cert.key",
                    sslCertFile = "cert.csr",
                 )

    compiler = VueCompiler(config.CompileFolder)
    argParser = ArgumentParser()
    argParser.addArgument(Argument("www", str))
    argParser.addArgument(Argument("save", str))
    argParser.addArgument(Argument("sslKey", str))
    argParser.addArgument(Argument("sslCert", str))
    argParser.addSwitch(Switch("rebuild"))
    argParser.addSwitch(Switch("debug"))

    argParser.parseArguments(sys.argv[1:])

    www = argParser.getParsedValue("www")
    save = argParser.getParsedValue("save")
    sslKey = argParser.getParsedValue("sslKey")
    sslCert = argParser.getParsedValue("sslCert")
    config.Debug = argParser.getParsedValue("debug")

    if www != None:
        config.RunningDirectory = str(www).rstrip("/")
    if save != None:
        config.SaveFileFolder = str(save).rstrip("/")
    if sslKey != None:
        config.SSLKeyPath = str(sslKey).rstrip("/")
    if sslCert != None:
        config.SSLCertPath = str(sslCert).rstrip("/")

    _root = logging.getLogger()
    _root.setLevel(logging.DEBUG)
    _fileFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s, %(filename)s:%(lineno)s")
    _consoleFormatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')

    _consoleHandler = logging.StreamHandler(sys.stdout)
    _consoleHandler.setFormatter(_consoleFormatter)
    #_consoleHandler.addFilter(ConsoleFilter())
    if config.Debug:
        _consoleHandler.setLevel(logging.DEBUG)
    else:
        _consoleHandler.setLevel(logging.WARNING)
        
    _fileHandler = logging.FileHandler(config.LogFilePath)
    _fileHandler.setLevel(logging.DEBUG)
    _fileHandler.setFormatter(_fileFormatter)
    _root.addHandler(_consoleHandler)
    _root.addHandler(_fileHandler)

    if argParser.getParsedValue("rebuild") or not os.path.exists(config.StandardPath):
        print("Starting (re)compiling procedure...")
        compiling = True
        compiler.StartCompile()

#import here for correct logging
from Home.Webserver.Server import HybridServer, HybridServerRequestHandler
import Home.Webserver.SSLCreator as SSLCreator
import Home.Webserver.Config.Setup.Import as Setup

#TODO logging

def main(config : Config, onServerCloseFunc : Callable[[], None]):
    print("Server starting on " + config.RunningDirectory + "...")
    webServer = HybridServer((config.HostAddress, config.ServerPort), RequestHandlerClass=HybridServerRequestHandler,virtualRootFile=config.RootFile, serviceableFileExtensions=config.ServeableFileExtensions, standardpath=config.StandardPath, runningDirectory=config.RunningDirectory)

    continueStart = True
    protocol = "http://"

    if not config.Debug:
        #TODO show correct tsl Version
        print("Activating TSL 1.3...")
        if config.TSLMinimumVersion != None:
            if TryActivateSSL(webServer, config):
                protocol = "https://"
            else:
                print("Could not activate TSL")
                continueStart = AskForYesOrNo("Do you want to continue without TSL?")

    if continueStart:
        PrintServerEndpoints(config, protocol)
        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            print("Server stopping...")
            onServerCloseFunc()
            webServer.server_close()
            print("Server stopped.")

    return continueStart

def AskForYesOrNo(message: str) -> bool:
    decision = True
    while True:
        i = input(message + " [(Y)es/(N)o]:").lower()
        if i == "y" or i == "yes":
            decision = True
            break
        elif i == "n" or i == "no":
            decision = False
            break
    
    return decision


def PrintServerEndpoints(config : Config, protocol : str):
    hostname = socket.gethostbyaddr(config.HostAddress)
    print("Server started on:")
    print("\t%s%s:%s" % (protocol, hostname[0], config.ServerPort))
    for name in hostname[1]:
        print("\t%s%s:%s" % (protocol, name, config.ServerPort))
    for ip in hostname[2]:
        print("\t%s%s:%s" % (protocol, ip, config.ServerPort))
        if ip == "127.0.0.1":
            print("\t%s%s:%s" % (protocol, "localhost", config.ServerPort))


def TryActivateSSL(webServer : HybridServer, config : Config) -> bool:
    activated = False
    try:
        if os.path.exists(config.SSLCertPath) and os.path.isfile(config.SSLCertPath) and os.path.exists(config.SSLKeyPath) and os.path.isfile(config.SSLKeyPath):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            #print(ssl.HAS_TLSv1_3)
            context.minimum_version = config.TSLMinimumVersion
            #TODO password
            context.load_cert_chain(certfile=config.SSLCertPath,keyfile=config.SSLKeyPath)

            webServer.socket = context.wrap_socket(webServer.socket, server_side=True)
            activated = True
        else:
            print("TSL Certificates not found")
            
            if SSLCreator.ImportResolved():
                if AskForYesOrNo("Do you want to create a new ssl certificate?"):
                    activated = CreateSSLCertInteractive(config=config)
                    if activated:
                        return TryActivateSSL(webServer=webServer, config=config)
                    else:
                        print("Could not create certificate")
            else:
                print("For automatically creating ssl certificates run command \"pip install pyOpenSSL\" or create the certificate and private key yourself and put them under: " + config.SSLCertPath + " and " + config.SSLKeyPath)
            activated = False

    except Exception as e:
        print(e)
        activated = False
                
    return activated
    
def CreateSSLCertInteractive(config : Config) -> bool:
    #TODO create with password
    created = False
    try:
        if not os.path.exists(config.SSLPath):
            os.makedirs(config.SSLPath)
        created = SSLCreator.Create(keyFile = config.SSLKeyPath, certFile = config.SSLCertPath)
        if created:
            print("New certificate: " + config.SSLCertPath)
            print("New private key: " + config.SSLKeyPath)
    except Exception as e:
        print("Error while creating new certificates")
        traceback.print_exc()
        #print(sys.exc_info()[2])
        print(e)
        created = False

    return created

def __onServerClose(config : Config):
    print("Closing Modules...")
    Setup.ServerModule.CloseModules(config)

if __name__ == "__main__":
    print("Starting modules...")
    Setup.ServerModule.InitModules(config)

    print("Loading data...")
    Setup.ServerModule.LoadModules(config)
    #Load(config, Setup)

    #TODO handle compile errors?
    if compiling:
        compilerOutput = compiler.Wait()
        compiling = False
        print("Compile procedure finished:")
        print()
        #https://stackoverflow.com/questions/12492810/python-how-can-i-make-the-ansi-escape-codes-to-work-also-in-windows
        #(probably) changes console mode to 7
        os.system("")
        for line in compilerOutput:
            printline = line.replace("\r\n", "").replace("\n", "")
            if(printline != ""):
                print("\t" + printline)
        print()
    #TODO set up saving thread
    if main(config=config, onServerCloseFunc=lambda : __onServerClose(config)) and not config.Debug:
        #after server closed, if no exception happens (except KeyboardInterrupt) and server was started: save
        print("Saving data...")
        if not os.path.exists(config.SaveFileFolder):
            os.makedirs(config.SaveFileFolder)
        Setup.ServerModule.SaveModules(config)
        config.Save()

