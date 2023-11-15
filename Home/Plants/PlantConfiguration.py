from ..Utils.ValueSpan import ValueSpan

class PlantConfiguration:
    
    def __init__(self, name : str, temperatureSpan : ValueSpan, moistureSpan : ValueSpan, conductivitySpan : ValueSpan, lightSpan : ValueSpan) -> None:
        self.__name : str = name
        self.__temperatureSpan : ValueSpan = temperatureSpan
        self.__moistureSpan : ValueSpan = moistureSpan
        self.__conductivitySpan : ValueSpan = conductivitySpan
        self.__lightSpan : ValueSpan = lightSpan

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def TemperatureSpan(self) -> ValueSpan:
        return self.__temperatureSpan

    @property
    def MoistureSpan(self) -> ValueSpan:
        return self.__moistureSpan

    @property
    def ConductivitySpan(self) -> ValueSpan:
        return self.__conductivitySpan
        
    @property
    def LightSpan(self) -> ValueSpan:
        return self.__lightSpan