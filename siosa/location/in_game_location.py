from siosa.location.location import Location
from siosa.location.resolution import Resolution


class InGameLocation(Location):
    def __init__(self, x1, y1, x2, y2, res: Resolution):
        """
        Creates an InGame location, which is always based on the
        screen resolution of the screen running the game. Not to be used outside
        of this module. Only factories should create this class as it serves
        as a type safety mechanism inside rest of the code.
        """
        super().__init__(x1, y1, x2, y2, res)
