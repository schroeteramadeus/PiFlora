class ValueSpan:
    def __init__(self, min, max) -> None:
        self.__min = min
        self.__max = max
    
    def BetweenInclude(self, value):
        return value >= self.Min and value <= self.Max

    def BetweenExclude(self, value):
        return value > self.Min and value < self.Max

    @property
    def Min(self):
        return self.__min

    @property
    def Max(self):
        return self.__max