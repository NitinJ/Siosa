import json
import os

from siosa.common.util import parent
from siosa.location.location_factory import LocationFactory


class StashCellLocation:
    _stash_cell_location_map = {}

    @staticmethod
    def _get_path(filename):
        """
        Args:
            filename:
        """
        siosa_base = parent(parent(__file__))
        return os.path.join(siosa_base, "resources/stash/{}".format(filename))

    @staticmethod
    def _get_stash_cell_location_map(is_quad):
        """
        Args:
            is_quad:
        """
        lf = LocationFactory()
        filename = 'quad.json' if is_quad else 'normal.json'
        filepath = StashCellLocation._get_path(filename)
        data = json.load(open(filepath, 'r'))
        ret = {}
        for key, location in data.items():
            cell = tuple(int(i) for i in key.split(","))
            ret[cell] = \
                lf.create(location[0], location[1], location[0], location[1])
        return ret

    @staticmethod
    def get_cell_location(is_quad, cell):
        """
        Args:
            is_quad:
            cell: Tuple (x, y)
        """
        cell = tuple(cell)
        if not StashCellLocation._stash_cell_location_map:
            StashCellLocation._stash_cell_location_map = \
                StashCellLocation._get_stash_cell_location_map(True)
        name = 'quad' if is_quad else 'normal'
        if name not in StashCellLocation._stash_cell_location_map.keys():
            StashCellLocation._stash_cell_location_map = \
                StashCellLocation._get_stash_cell_location_map(is_quad)
        return StashCellLocation._stash_cell_location_map[cell]


if __name__ == "__main__":
    print(StashCellLocation.get_cell_location(True, (0, 0)))