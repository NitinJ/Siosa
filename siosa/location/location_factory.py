from siosa.common.singleton import Singleton
from siosa.location.in_game_location import InGameLocation


class LocationFactory(metaclass=Singleton):
    def __init__(self, res_x=1920, res_y=1080):
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
            int(location.y1 * self.res_y / 1080), 
            int(location.x2 * self.res_x / 1920), 
            int(location.y2 * self.res_y / 1080))

    def get_center_of_screen(self):
        return InGameLocation(self.res_x/2, self.res_y/2, self.res_x/2, self.res_y/2)

class Locations:
    SCREEN_CENTER = InGameLocation(1920/2, 1080/2, 1920/2, 1080/2)
    # Currency tab
    CURRENCY_CENTER = InGameLocation(295, 396, 371, 555)
    CURRENCY_ALTERATION = InGameLocation(98, 275, 131, 311)
    CURRENCY_AUGMENT = InGameLocation(217, 329, 245, 359)
    # Decorations
    EDIT_HIDEOUT_ARROW = InGameLocation(1172, 1043, 1185, 1058)
    EDIT_HIDEOUT_DOWN_ARROW = InGameLocation(1172, 924, 1187, 937)
    EDIT_HIDEOUT_BUTTON = InGameLocation(1008, 963, 1064, 1035)
    OPEN_DECORATIONS_BUTTON = InGameLocation(1095, 960, 1143, 999)
    STASH_DECORATION = InGameLocation(1416, 468, 1496, 542)
    CLOSE_DECORATIONS_BUTTON = InGameLocation(1879, 60, 1892, 74)
    CLOSE_STASH_BUTTON = InGameLocation(620, 57, 636, 77)
    # Stash
    FIRST_STASH_TAB_RIGHT_LIST = InGameLocation(693, 136, 855, 152)
    # Inventory
    INVENTORY = InGameLocation(1260, 579, 1915, 861)
    INVENTORY_0_0 = InGameLocation(1274, 590, 1324, 640)
    INVENTORY_DIVIDER_HORIZONTAL = InGameLocation(1283, 638, 1315, 644)
    INVENTORY_DIVIDER_VERTICAL = InGameLocation(1321, 599, 1327, 631)
    # Player items
    CHEST_PEICE = InGameLocation(1577, 269, 1596, 288)
    # Banners
    STASH_BANNER = InGameLocation(288, 56, 375, 81)
