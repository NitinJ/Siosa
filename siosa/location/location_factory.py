import pyautogui

from siosa.common.singleton import Singleton
from siosa.location.in_game_location import InGameLocation
from siosa.location.location import Location
from siosa.location.resolution import Resolutions, Resolution


class LocationFactoryBase(metaclass=Singleton):
    def __init__(self, resolution=Resolutions.p1080):
        self.resolution = resolution

    def get(self, location: Location) -> InGameLocation:
        return self._get_in_game_location(location)

    def create(self, x1, y1, x2, y2) -> InGameLocation:
        return self._get_in_game_location(
            Location(x1, y1, x2, y2, self.resolution))

    def _get_in_game_location(self, location):
        # Scales the given location to the location factory's resolution.
        scaled_location = LocationFactoryBase._scale_to_resolution(
            location, self.resolution)
        return InGameLocation(scaled_location.x1, scaled_location.y1,
                              scaled_location.x2, scaled_location.y2,
                              LocationFactoryBase._get_unique_name(location))

    @staticmethod
    def _get_unique_name(location):
        """
        Returns the unique name for a given location by using it's coordinates
        in 1080p resolution.
        Args:
            location: The location for which the unique name is required.

        Returns: The unique name for a location

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
        """
        Scales a given location to a given resolution.
        Args:
            location: Location to scale to a given resolution .
            resolution: The resolution to scale the given location to.

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
    SCREEN_CENTER = Location(Resolutions.p1080.w / 2, Resolutions.p1080.h / 2,
                             Resolutions.p1080.w / 2, Resolutions.p1080.h / 2,
                             Resolutions.p1080)

    # Currency tab
    CURRENCY_CENTER = Location(295, 396, 371, 555, Resolutions.p1080)
    CURRENCY_ALTERATION = Location(98, 275, 131, 311, Resolutions.p1080)
    CURRENCY_AUGMENT = Location(217, 329, 245, 359, Resolutions.p1080)

    # Decorations
    EDIT_HIDEOUT_ARROW = Location(1172, 1043, 1185, 1058, Resolutions.p1080)
    EDIT_HIDEOUT_DOWN_ARROW = Location(1172, 924, 1187, 937, Resolutions.p1080)
    EDIT_HIDEOUT_BUTTON = Location(1008, 963, 1064, 1035, Resolutions.p1080)
    OPEN_DECORATIONS_BUTTON = Location(1095, 960, 1143, 999, Resolutions.p1080)
    STASH_DECORATION = Location(1416, 468, 1496, 542, Resolutions.p1080)
    CLOSE_DECORATIONS_BUTTON = Location(1879, 60, 1892, 74, Resolutions.p1080)
    CLOSE_STASH_BUTTON = Location(620, 57, 636, 77, Resolutions.p1080)

    # Stash
    FIRST_STASH_TAB_RIGHT_LIST = Location(690, 134, 860, 154, Resolutions.p1080)
    NORMAL_STASH_0_0 = Location(19, 162, 69, 213, Resolutions.p1080)
    QUAD_STASH_0_0 = Location(17, 163, 42, 187, Resolutions.p1080)
    STASH_TAB = Location(19, 162, 648, 792, Resolutions.p1080)

    # Inventory
    INVENTORY = Location(1260, 579, 1915, 861, Resolutions.p1080)
    INVENTORY_0_0 = Location(1274, 590, 1324, 640, Resolutions.p1080)
    INVENTORY_0_0_WITH_RIGHT_BORDER = Location(1274, 590, 1327, 640, Resolutions.p1080)
    INVENTORY_0_0_WITH_BOTTOM_BORDER = Location(1274, 590, 1324, 643, Resolutions.p1080)
    INVENTORY_DIVIDER_HORIZONTAL = Location(1283, 638, 1315, 644, Resolutions.p1080)
    INVENTORY_DIVIDER_VERTICAL = Location(1321, 599, 1327, 631, Resolutions.p1080)

    # Player items
    CHEST_PIECE = Location(1577, 269, 1596, 288, Resolutions.p1080)

    # Banners
    STASH_BANNER = Location(288, 56, 375, 81, Resolutions.p1080)
