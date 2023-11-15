from numbers import Number

class ValueSpan:
    def __init__(self, min : Number, max : Number) -> None:
        self.__min : Number = min
        self.__max : Number = max
    
    def BetweenInclude(self, value : Number) -> bool:
        return value >= self.Min and value <= self.Max

    def BetweenExclude(self, value : Number) -> bool:
        return value > self.Min and value < self.Max

    @property
    def Min(self) -> Number:
        return self.__min

    @property
    def Max(self) -> Number:
        return self.__max