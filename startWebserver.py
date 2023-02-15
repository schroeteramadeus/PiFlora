import logging
from Home.Utils.ArgumentParser import Argument, ArgumentParser, Switch 
from Config.Config import Config
import os
import ssl
import sys
from typing import Callable
#from ConsoleFilter import ConsoleFilter
import socket

if __name__ == "__main__":
    config = Config()

    argParser = ArgumentParser()
    argParser.addArgument(Argument("www", str))
    argParser.addArgument(Argument("save", str))
    argParser.addArgument(Argument("sslKey", str))
    argParser.addArgument(Argument("sslCert", str))
    argParser.addSwitch(Switch("debug"))

    argParser.parseArguments(sys.argv[1:])

    www = argParser.getParsedValue("www")
    save = argParser.getParsedValue("save")
    sslKey = argParser.getParsedValue("sslKey")
    sslCert = argParser.getParsedValue("sslCert")
    debug = argParser.getParsedValue("debug")

    if www != None:
        config.RunningDirectory = str(www).rstrip("/")
    if save != None:
        config.SaveFileFolder = str(save).rstrip("/")
    if sslKey != None:
        config.SSLKeyPath = str(sslKey).rstrip("/")
    if sslCert != None:
        config.SSLCertPath = str(sslCert).rstrip("/")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')

    _consoleHandler = logging.StreamHandler(sys.stdout)
    _consoleHandler.setFormatter(formatter)
    #_consoleHandler.addFilter(ConsoleFilter())
    if debug:
        _consoleHandler.setLevel(logging.DEBUG)
    else:
        _consoleHandler.setLevel(logging.WARNING)
        
    root.addHandler(_consoleHandler)


from Home.Webserver.Server import HybridServer, HybridServerRequestHandler
from Home.Webserver.VirtualFile import VirtualFile
import Home.Webserver.SSLCreator as SSLCreator
import Config.Setup.Import as Setup

#TODO logging

def main(config : Config, virtualRootFile : VirtualFile, onServerCloseFunc : Callable[[], None], debug = False):
    print("Server starting on " + config.RunningDirectory + "...")
    webServer = HybridServer((config.HostAddress, config.ServerPort), RequestHandlerClass=HybridServerRequestHandler,virtualRootFile=virtualRootFile, serviceableFileExtensions=config.ServeableFileExtensions, standardpath=config.StandardPath, runningDirectory=config.RunningDirectory)

    continueStart = True
    protocol = "http://"

    if not debug:
        print("Activating TLS 1.3...")
        if config.TSLMinimumVersion != None:
            if TryActivateSSL(webServer, config):
                protocol = "https://"
            else:
                print("Could not activate TLS")
                continueStart = AskForYesOrNo("Do you want to continue without TLS?")

    if continueStart:
        PrintServerEndpoints(config, protocol)
        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            onServerCloseFunc()
            webServer.server_close()
            print("Server stopped.")

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
    #TODO interactive
    created = False
    try:
        created = SSLCreator.Create(keyFile = config.SSLKeyPath, certFile = config.SSLCertPath)
        print("New certificate: " + config.SSLCertPath)
        print("New private key: " + config.SSLKeyPath)
    except Exception as e:
        print("Error while creating new certificates")
        print(e)
        created = False

    return created

def __onServerClose():
    print("Closing Modules...")
    Setup.ServerModule.CloseModules()

if __name__ == "__main__":
    print("Starting modules...")
    Setup.ServerModule.InitModules(debug)

    print("Loading data...")
    Setup.ServerModule.LoadModules(config.SaveFileFolder)
    #Load(config, Setup)

    #TODO set up saving thread
    main(config=config, virtualRootFile=Setup.SystemModule.Get().RootFile, onServerCloseFunc=__onServerClose,debug=debug)
    #if no exception happens (except KeyboardInterrupt): save
    if not debug:
        print("Saving data...")
        Setup.ServerModule.SaveModules(config.SaveFileFolder)
        #Save(config, Setup)

