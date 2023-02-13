from ..Utils.ValueSpan import ValueSpan

class PlantConfiguration:
    
    def __init__(self, name, temperatureSpan, moistureSpan, conductivitySpan, lightSpan) -> None:
        #type: (str, ValueSpan, ValueSpan, ValueSpan, ValueSpan) -> None
        self.__name = name#type: str
        self.__temperatureSpan = temperatureSpan#type: ValueSpan
        self.__moistureSpan = moistureSpan#type: ValueSpan
        self.__conductivitySpan = conductivitySpan#type: ValueSpan
        self.__lightSpan = lightSpan#type: ValueSpan

    @property
    def Name(self):
        return self.__name

    @property
    def TemperatureSpan(self):
        return self.__temperatureSpan

    @property
    def MoistureSpan(self):
        return self.__moistureSpan

    @property
    def ConductivitySpan(self):
        return self.__conductivitySpan
        
    @property
    def LightSpan(self):
        return self.__lightSpan