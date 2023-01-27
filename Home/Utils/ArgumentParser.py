#VERSION: Python 3.*
from typing import Any, List

class Argument:
    __name = str()
    __argType = type

    def __init__(self, name:str,argType:type):
        self.__name = name
        self.__argType = argType

    @property
    def Name(self) -> str:
        return self.__name
    @property
    def Type(self) -> type:
        return self.__argType

class Switch:
    __name = str()

    def __init__(self, name:str):
        self.__name = name
    
    @property
    def Name(self) -> str:
        return self.__name

class ArgumentParser:
    __arguments = [Argument]
    __switches = [Switch]

    __parsed = dict()

    def addSwitch(self, switch:Switch):
        self.__switches.append(switch)
        self.__parsed[switch.Name] = False

    def addArgument(self, argument:Argument):
        self.__arguments.append(argument)
        self.__parsed[argument.Name] = None

    def parseArguments(self, args:List[str]):
        #region clear
        for switch in self.__switches:
            self.__parsed[switch.Name] = False
        for argument in self.__arguments:
            self.__parsed[argument.Name] = None
        #endregion clear

        #region parse
        for switch in self.__switches:
            if(args.count("-" + switch.Name) > 0):
                self.__parsed[switch.Name] = True
        
        for argument in self.__arguments:
            if(args.count("-" + argument.Name) > 0):
                arg = args[args.index("-" + argument.Name) + 1]
                #TODO add typing
                self.__parsed[argument.Name] = arg
        #endregion parse
    
    def getParsedValue(self, name:str):
        return self.__parsed[name]
