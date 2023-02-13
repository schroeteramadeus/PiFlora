
from abc import abstractmethod
from ..Actor import Actor

class Pump(Actor):

    @abstractmethod
    def __init__(self) -> None:
        super().__init__()

    def Act(self, data):
        #type: (dict[str, object]) -> dict[str, object]
        if "water" in data:
            return {
                "water": self.Water(data["water"]),
            }
        return {"water":0}

    @abstractmethod
    #return: float for actual water flown
    def Water(self, ml):
        #type: (float) -> float
        pass