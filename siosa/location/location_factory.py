import logging

import pyautogui

from siosa.common.singleton import Singleton
from siosa.location.in_game_location import InGameLocation
from siosa.location.location import Location
from siosa.location.resolution import Resolutions, Resolution


class LocationFactoryBase(metaclass=Singleton):
    def __init__(self, resolution=Resolutions.p1080):
        """
        Args:
            resolution:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.resolution = resolution

        self.logger.debug("Created with resolution : {}".format(
            str(self.resolution)))

    def get(self, location: Location) -> InGameLocation:
        """
        Args:
            location (Location):
        """
        return self._get_in_game_location(location)

    def create(self, x1, y1, x2, y2) -> InGameLocation:
        """Creates an in game location from a given set of bounding box
        co-ordinates. Returns: The InGameLocation

        Args:
            x1:
            y1:
            x2:
            y2:
        """
        return self._get_in_game_location(
            Location(x1, y1, x2, y2, self.resolution))

    def _get_in_game_location(self, location):
        # Scales the given location to the location factory's resolution.
        """
        Args:
            location:
        """
        scaled_location = LocationFactoryBase._scale_to_resolution(
            location, self.resolution)
        return InGameLocation(scaled_location.x1, scaled_location.y1,
                              scaled_location.x2, scaled_location.y2,
                              LocationFactoryBase._get_unique_name(location))

    @staticmethod
    def _get_unique_name(location):
        """Returns the unique name for a given location by using it's
        coordinates in 1080p resolution. :param location: The location for which
        the unique name is required.

        Returns: The unique name for a location

        Args:
            location:
        """
        scaled_location_p1080 = LocationFactoryBase._scale_to_resolution(
            location,
            Resolutions.p1080)
        return "{}.{}.{}.{}.{}.{}".format(
            location.resolution.w,
            location.resolution.h,
            scaled_location_p1080.x1,
            scaled_location_p1080.y1,
            scaled_location_p1080.x2,
            scaled_location_p1080.y2)

    @staticmethod
    def _scale_to_resolution(location, resolution):
        """Scales a given location to a given resolution. :param location:
        Location to scale to a given resolution . :param resolution: The
        resolution to scale the given location to.

        Args:
            location:
            resolution:

        Returns:
            Scaled location
        """
        w_ratio = resolution.w / location.resolution.w
        h_ratio = resolution.h / location.resolution.h
        return Location(
            int(location.x1 * w_ratio),
            int(location.y1 * h_ratio),
            int(location.x2 * w_ratio),
            int(location.y2 * h_ratio),
            resolution,
            location.name)


class LocationFactory(LocationFactoryBase):
    """Location factory should be used for getting locations across the app. No
    location should be used directly as those might not be for the current
    resolution.
    """

    def __init__(self):
        size = pyautogui.size()
        current = Resolution(size[0], size[1])
        super().__init__(resolution=current)


class Locations:
    SCREEN_FULL = Location(0, 0,
                           Resolutions.p1080.w, Resolutions.p1080.h,
                           Resolutions.p1080)
    SCREEN_CENTER = Location(Resolutions.p1080.w / 2, Resolutions.p1080.h / 2,
                             Resolutions.p1080.w / 2, Resolutions.p1080.h / 2,
                             Resolutions.p1080)
    SCREEN_NOOP_POSITION = Location(1342, 478, 1384, 522, Resolutions.p1080)
    SCREEN_RIGHT_STRIP = Location(1870, 0, 1920, 1080, Resolutions.p1080)

    # Currency tab
    CURRENCY_CENTER = Location(295, 366, 371, 525, Resolutions.p1080)
    CURRENCY_ALTERATION = Location(98, 245, 131, 281, Resolutions.p1080)
    CURRENCY_AUGMENT = Location(217, 299, 245, 329, Resolutions.p1080)
    CURRENCY_REGAL = Location(413, 241, 451, 279, Resolutions.p1080)
    CURRENCY_SCOURING = Location(157, 423, 195, 461, Resolutions.p1080)
    CURRENCY_TRANSMUTATION = Location(39, 242, 77, 280, Resolutions.p1080)

    # Decorations
    DECORATIONS_BANNER = Location(1503, 56, 1674, 81,
                                              Resolutions.p1080)
    DECORATIONS_EDIT_HIDEOUT_ARROW = Location(1172, 1043, 1185, 1058, Resolutions.p1080)
    DECORATIONS_EDIT_HIDEOUT_DOWN_ARROW = Location(1172, 924, 1187, 937, Resolutions.p1080)
    DECORATIONS_EDIT_HIDEOUT_BUTTON = Location(1008, 963, 1064, 1035, Resolutions.p1080)
    DECORATIONS_OPEN_BUTTON = Location(1095, 960, 1143, 999, Resolutions.p1080)
    DECORATIONS_STASH_AFTER_SEARCHING = Location(1409, 232, 1498, 322, Resolutions.p1080)
    DECORATIONS_CLOSE_BUTTON = Location(1879, 60, 1892, 74, Resolutions.p1080)
    DECORATIONS_UTILITIES_ARROW = Location(1291, 180, 1318, 212, Resolutions.p1080)

    # Stash
    STASH_CLOSE_BUTTON = Location(620, 57, 636, 77, Resolutions.p1080)
    STASH_FIRST_TAB_RIGHT_LIST = Location(764, 111, 764, 111, Resolutions.p1080)
    STASH_NORMAL_0_0 = Location(20, 130, 68, 178, Resolutions.p1080)
    STASH_QUAD_0_0 = Location(18, 129, 42, 153, Resolutions.p1080)
    STASH_TAB = Location(18, 129, 648, 758, Resolutions.p1080)
    STASH = Location(980, 414, 1025, 424, Resolutions.p1080)
    STASH_BANNER = Location(288, 56, 375, 81, Resolutions.p1080)

    # Inventory
    INVENTORY = Location(1260, 579, 1915, 861, Resolutions.p1080)
    INVENTORY_0_0 = Location(1273, 590, 1323, 640, Resolutions.p1080)
    INVENTORY_0_0_WITH_RIGHT_BORDER = Location(1273, 590, 1325, 640, Resolutions.p1080)
    INVENTORY_0_0_WITH_BOTTOM_BORDER = Location(1273, 590, 1323, 642, Resolutions.p1080)
    INVENTORY_ROW1 = Location(1273, 590, 1903, 640, Resolutions.p1080)
    INVENTORY_BANNER = Location(1520, 58, 1650, 80, Resolutions.p1080)

    # Player items
    PLAYER_ITEMS_CHEST_PIECE = Location(1577, 269, 1596, 288, Resolutions.p1080)

    # Trade
    TRADE_AWAITING_TRADE_BOX = Location(714, 568, 1203, 601, Resolutions.p1080)
    TRADE_AWAITING_TRADE_CANCEL_BUTTON = Location(1054, 544, 1176, 572, Resolutions.p1080)
    TRADE_WINDOW_TITLE = Location(541, 78, 713, 114, Resolutions.p1080)

    TRADE_WINDOW_ME = Location(309, 533, 944, 799, Resolutions.p1080)
    TRADE_WINDOW_ME_0_0 = Location(312, 536, 363, 587, Resolutions.p1080)
    TRADE_WINDOW_ME_EMPTY_TEXT = Location(469, 658, 785, 676, Resolutions.p1080)

    TRADE_WINDOW_OTHER = Location(308, 200, 947, 471, Resolutions.p1080)
    TRADE_WINDOW_OTHER_0_0 = Location(313, 206, 363, 256, Resolutions.p1080)
    TRADE_WINDOW_OTHER_ROW1 = Location(311, 204, 942, 256, Resolutions.p1080)
    TRADE_WINDOW_OTHER_0_0_COUNT = Location(315, 206, 336, 225, Resolutions.p1080)
    TRADE_WINDOW_OTHER_SMALL_0_0 = Location(328, 222, 348, 241, Resolutions.p1080)

    TRADE_WINDOW_MOUSEOVER_WARNING_TEXT = Location(492, 828, 537, 842, Resolutions.p1080)
    TRADE_ACCEPT_RETRACTED = Location(383, 821, 404, 850, Resolutions.p1080)
    TRADE_ACCEPT_GREEN_AURA = Location(349, 470, 397, 524, Resolutions.p1080)
    TRADE_ACCEPT_GREEN_AURA_ME = Location(299, 509, 347, 541, Resolutions.p1080)
    TRADE_CANCEL_ACCEPT_BUTTON = Location(307, 821, 448, 849, Resolutions.p1080)
    TRADE_ACCEPT_BUTTON = Location(307, 821, 448, 849, Resolutions.p1080)
    TRADE_WINDOW_FULL = Location(284, 75, 969, 869, Resolutions.p1080)
    TRADE_WINDOW_CLOSE_BUTTON = Location(929, 82, 959, 112, Resolutions.p1080)

    PARTY_NOTIFICATIONS_CLOSE_BUTTON = Location(1892, 700, 1900, 727, Resolutions.p1080)
    PARTY_NOTIFICATIONS_AREA = Location(1875, 585, 1920, 860, Resolutions.p1080)

    PRICE_ITEM_WINDOW_ARROW = Location(157, 251, 189, 283, Resolutions.p1080)
