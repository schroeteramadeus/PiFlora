import Home.Utils.ValueSpan as VS

class PlantConfiguration:
    
    def __init__(self, name, temperatureSpan, moistureSpan, conductivitySpan, lightSpan) -> None:
        #type: (str, VS.ValueSpan, VS.ValueSpan, VS.ValueSpan, VS.ValueSpan) -> None
        self.__name = name#type: str
        self.__temperatureSpan = temperatureSpan#type: VS.ValueSpan
        self.__moistureSpan = moistureSpan#type: VS.ValueSpan
        self.__conductivitySpan = conductivitySpan#type: VS.ValueSpan
        self.__lightSpan = lightSpan#type: VS.ValueSpan

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