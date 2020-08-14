from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_step import Step
from siosa.location.location_factory import LocationFactory, Locations


class ScanInventory(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
        self.clipboard = PoeClipboard()
        self.items = []
    
    def execute(self):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.mc.move_mouse(self._get_location(0, 0))
        item = self.clipboard.read_item_at_cursor()
        for col in xrange(0, 12):
            for row in xrange(0, 5):
                self.mc.move_mouse(self._get_location(row, col))
                item = self.clipboard.read_item_at_cursor()
                self.items.append(item)

    def _get_location(self, r, c):
        # Invent box size
        size = 55
        x = Locations.INVENTORY_0_0.x1
        y = Locations.INVENTORY_0_0.y1
        x2 = x + c * size
        y2 = y + r * size
        return LocationFactory.get_instance().create(x2, y2, x2, y2)
