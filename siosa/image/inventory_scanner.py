from siosa.image.template_matcher import TemplateMatcher
from siosa.location.location_factory import Locations


class InventoryScanner:
    def __init__(self):
        self.tm = TemplateMatcher(Locations.INVENTORY_0_0, debug=True)

    def scan(self):
        points = self.tm.match(Locations.INVENTORY)
        return self._convert_points_to_inventory_positions(points)

    def _convert_points_to_inventory_positions(self, points):
        min_x = min([p[0] for p in points])
        min_y = min([p[1] for p in points])
        width = Locations.INVENTORY_0_0.get_width()
        height = Locations.INVENTORY_0_0.get_height()
        positions = {}
        for p in points:
            pos_x = (p[1] - min_y) // height
            pos_y = (p[0] - min_x) // width
            positions[(pos_x, pos_y)] = 1
        return positions
