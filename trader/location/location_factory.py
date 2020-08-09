from common.singleton import Singleton
from in_game_location import InGameLocation

class LocationFactory(Singleton):
    def __init__(self, res_x=1920, res_y=1020):
        Singleton.__init__(self)
        self.res_x = res_x
        self.res_y = res_y

    def get(self, location):
        return self._create_internal(location)

    def create(self, x1, y1, x2, y2):
        return self._create_internal(InGameLocation(x1, y1, x2, y2))

    def _create_internal(self, location):
        return self._scale_to_res(location)

    def _scale_to_res(self, location):
        # Scales the internal locations to the given resolution
        return InGameLocation(
            int(location.x1 * self.res_x / 1920), 
            int(location.y1 * self.res_y / 1020), 
            int(location.x2 * self.res_x / 1920), 
            int(location.y2 * self.res_y / 1020))

    def get_center_of_screen(self):
        return InGameLocation(self.res_x/2, self.res_x/2, self.res_y/2, self.res_y/2)

class Locations:
    CURRENCY_CENTER = InGameLocation(295, 396, 371, 555)
    CURRENCY_ALTERATION = InGameLocation(98, 275, 131, 311)
    CURRENCY_AUGMENT = InGameLocation(217, 329, 245, 359)
