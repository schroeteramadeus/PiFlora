import logging
import os
import ssl
import sys
from ConsoleFilter import ConsoleFilter
from Home.Webserver.Server import HybridServer, HybridServerRequestHandler
import Home.Webserver.SSLCreator as SSLCreator
from Home.Utils.ArgumentParser import Argument, ArgumentParser 
import socket

import Config.Setup.Import as Setup
from Config.Config import Config

def main(config : Config):

    print("Loading data...")
    Load(config)
    print("Server starting on " + config.RunningDirectory)
    webServer = HybridServer((config.HostAddress, config.ServerPort), RequestHandlerClass=HybridServerRequestHandler,virtualRootFile=Setup.ROOTFILE, serviceableFileExtensions=config.ServeableFileExtensions, standardpath=config.StandardPath, runningDirectory=config.RunningDirectory)

    continueStart = True
    protocol = "http://"
    print("Activating TLS 1.3")
    if config.TSLMinimumVersion != None:
        if TryActivateSSL(webServer, config):
            protocol = "https://"
        else:
            print("Could not activate TLS")
            continueStart = AskForYesOrNo("Do you want to continue without TLS?")

    if continueStart:
        PrintServerEndpoints(config, protocol)

        #TODO set up saving thread
        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            if Setup.PLANTMANAGER != None and Setup.PLANTMANAGER.IsRunning:
                Setup.PLANTMANAGER.Stop()
            if Setup.BLUETOOTHMANAGER != None and Setup.BLUETOOTHMANAGER.IsRunning():
                Setup.BLUETOOTHMANAGER.Stop()
            if not Setup.PLANTMANAGER.IsDebug:
                Save(config)
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
                    activated = CreateSSLCertInteractive(certfile=config.SSLCertPath,keyfile=config.SSLKeyPath)
                    if activated:
                        return TryActivateSSL(webServer=webServer, config=config)
                    else:
                        print("Could not create certificate")
            else:
                print("For automatically creating ssl certificates run command \"pip install pyOpenSSL\" or create the certificate and private key yourself and put them under: " + config.SSLCertPath + " and " + config.SSLKeyPath)
            activated = False

    except Exception as e:
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
    
def Save(config : Config):
    Setup.ONSAVE(config.SaveFileFolder)

def Load(config : Config):
    Setup.ONLOAD(config.SaveFileFolder)

if __name__ == "__main__":   

    #TODO try load config

    config = Config()
    #TODO TEST REMOVE LATER
    config.TSLMinimumVersion = None

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
        config.RunningDirectory = str(www).rstrip("/")
    if save != None:
        config.SaveFileFolder = str(save).rstrip("/")
    if sslKey != None:
        config.SSLKeyPath = str(sslKey).rstrip("/")
    if sslCert != None:
        config.SSLCertPath = str(sslCert).rstrip("/")

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.addFilter(ConsoleFilter())

    root.addHandler(handler)

    main(config)