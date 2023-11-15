#VERSION: Python 3.*
from typing import Any, List

class Argument:
    __name : str = None
    __argType : type = None

    def __init__(self, name:str,argType:type):
        self.__name : str = name
        self.__argType : type = argType

    @property
    def Name(self) -> str:
        return self.__name
    @property
    def Type(self) -> type:
        return self.__argType

class Switch:
    __name : str = None

    def __init__(self, name:str):
        self.__name : str = name
    
    @property
    def Name(self) -> str:
        return self.__name

class ArgumentParser:
    __arguments : list[Argument] = []
    __switches : list[Switch] = []

    __parsed : dict[str, str | bool | None] = {}

    def addSwitch(self, switch:Switch) -> None:
        self.__switches.append(switch)
        self.__parsed[switch.Name] = False

    def addArgument(self, argument:Argument) -> None:
        self.__arguments.append(argument)
        self.__parsed[argument.Name] = None

    def parseArguments(self, args:List[str]) -> None:
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
    
    def getParsedValue(self, name:str) -> str | bool | None:
        return self.__parsed[name]