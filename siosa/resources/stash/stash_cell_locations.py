import json

from siosa.location.location_factory import LocationFactory


class StashCellLocation:
    _stash_cell_location_map = {}

    @staticmethod
    def _get_stash_cell_location_map(is_quad):
        lf = LocationFactory()
        filename = 'quad.json' if is_quad else 'normal.json'
        data = json.load(open(filename, 'r'))
        ret = {}
        for key, location in data.items():
            cell = tuple(int(i) for i in key.split(","))
            ret[cell] = \
                lf.create(location[0], location[1], location[0], location[1])
        return ret

    @staticmethod
    def get_cell_location(is_quad, cell):
        name = 'quad' if is_quad else 'normal'
        if name not in StashCellLocation._stash_cell_location_map.keys():
            StashCellLocation._stash_cell_location_map = \
                StashCellLocation._get_stash_cell_location_map(is_quad)
        return StashCellLocation._stash_cell_location_map[cell]
