from ..common.decorations import singleton
from location import Location

@singleton
class LocationFactory:
    def __init__(self, res_x=1920, res_y=1020):
        self.res_x = res_x
        self.res_y = res_y

    def get(self, location):
        return self._create_internal(location)

    def create(self, x1, y1, x2, y2):
        return self._create_internal(Location(x1, y1, x2, y2))

    def _create_internal(self, location):
        return self._scale_to_res(location)

    def _scale_to_res(self, location):
        # Scales the internal locations to the given resolution
        return Location(
            int(location.x1 * self.res_x / 1920), 
            int(location.y1 * self.res_y / 1020), 
            int(location.x2 * self.res_x / 1920), 
            int(location.y2 * self.res_y / 1020))

class Locations:
    CURRENCY_CENTER = Location(295, 396, 371, 555)
    CURRENCY_ALTERATION = Location(98, 275, 131, 311)
    CURRENCY_AUGMENT = Location(217, 329, 245, 359)