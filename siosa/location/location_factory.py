import json
import logging
import os

from siosa.common.singleton import Singleton
from siosa.common.util import parent
from siosa.control.window_controller import WindowController
from siosa.location.in_game_location import InGameLocation
from siosa.location.location import Location
from siosa.location.resolution import Resolutions, Resolution


class LocationFactoryBase(metaclass=Singleton):
    def __init__(self, resolution: Resolution = Resolutions.p1080.value):
        """
        Args:
            resolution: THe screen resolution.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.resolution = resolution
        self.logger.debug("Created with resolution : {}".format(
            str(self.resolution)))

    def get(self, location: Location) -> InGameLocation:
        return InGameLocation(
            location.x1, location.y1, location.x2, location.y2,
            location.resolution).get_scaled_for_resolution(self.resolution)

    def create(self, x1, y1, x2, y2) -> InGameLocation:
        return InGameLocation(x1, y1, x2, y2, self.resolution)


class LocationFactory(LocationFactoryBase):
    """
    Location factory should be used for getting locations across the app. No
    location should be used directly as those might not be for the current
    resolution.
    This class provides location objects for various supported base locations.
    Location coordinates are stored in resources for each supported base res.
    LocationFactory also initializes Locations objects throughout the code based
    on the passed in resolution or the current screen resolution
    """

    def __init__(self, resolution: Resolution = None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.locations_map_ = {}
        if not resolution:
            resolution = self._find_screen_resolution()

        self.base_resolution = resolution.get_base_resolution()
        if not self.base_resolution:
            # Resolution not supported, app cannot function.
            raise Exception("Resolution not supported !")

        super().__init__(resolution=resolution)
        Locations.init(self)

    def _find_screen_resolution(self):
        wc = WindowController()
        dim = wc.get_poe_monitor_dimensions()
        self.logger.debug("Monitor number: {}, monitor_info: {}".format(
            wc.get_mss_monitor(), dim))
        size = (dim[2], dim[3])
        return Resolution(size[0], size[1])

    def get_base_location(self, location_str) -> Location:
        """
        Returns the location for a given location string, in the screen's base
        resolution.
        Args:
            location_str: Location string

        Returns: The Location wrt base resolution.

        """
        if not self.locations_map_:
            self._load_locations_map()
        coordinates = self.locations_map_[location_str]
        return Location(
            coordinates[0], coordinates[1], coordinates[2], coordinates[3],
            self.base_resolution)

    def _get_locations_file_path(self):
        siosa_base = parent(parent(__file__))
        return os.path.join(siosa_base,
                            "resources\\locations\\{}.json".format(
                                str(self.base_resolution)))

    def _load_locations_map(self):
        data = json.load(open(self._get_locations_file_path(), 'r'))
        self.locations_map_ = data['locations']


class Locations:
    # Full screen locations
    SCREEN_FULL = None
    SCREEN_CENTER = None
    SCREEN_NOOP_POSITION = None
    PARTY_NOTIFICATIONS_AREA = None

    # Currency Tab
    ITEM_LOCATION = None
    CURRENCY_ALTERATION = None
    CURRENCY_AUGMENTATION = None
    CURRENCY_REGAL = None
    CURRENCY_SCOURING = None
    CURRENCY_TRANSMUTATION = None
    CURRENCY_CHANCE = None
    CURRENCY_CHAOS = None
    CURRENCY_ALCHEMY = None

    # Decorations
    DECORATIONS_PANE = None
    DECORATIONS_EDIT_BOX = None
    DECORATIONS_EDIT_HIDEOUT_ARROW = None
    DECORATIONS_EDIT_HIDEOUT_DOWN_ARROW = None
    DECORATIONS_EDIT_HIDEOUT_BUTTON = None
    DECORATIONS_OPEN_BUTTON = None
    DECORATIONS_STASH_AFTER_SEARCHING = None
    DECORATIONS_CLOSE_BUTTON = None
    DECORATIONS_UTILITIES_ARROW = None

    # Stash tab
    STASH_FIRST_TAB_RIGHT_LIST = None
    STASH_NORMAL_0_0 = None
    STASH_QUAD_0_0 = None
    STASH_TAB = None
    STASH_PANE = None
    STASH_BANNER = None

    # Inventory
    INVENTORY = None
    INVENTORY_PANE = None
    INVENTORY_0_0 = None
    INVENTORY_BANNER = None

    # Trade and vendor window
    TRADE_AWAITING_TRADE_CANCEL_BUTTON = None
    TRADE_WINDOW_OTHER = None
    TRADE_WINDOW_OTHER_0_0 = None
    TRADE_ACCEPT_GREEN_AURA_BOX = None
    TRADE_ACCEPT_BUTTON = None
    TRADE_WINDOW_FULL = None
    VENDOR_TRADE_ACCEPT_BUTTON = None

    @staticmethod
    def init(location_factory):
        # Full screen locations
        for static_location_str in dir(Locations):
            if not static_location_str.startswith("__") and \
                    static_location_str != "init":
                setattr(Locations, static_location_str,
                        location_factory.get_base_location(static_location_str))
