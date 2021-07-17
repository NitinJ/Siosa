import logging

from siosa.location.location import Location
from siosa.location.location_factory import LocationFactory


class Grid:
    """Scans any grid for items. Takes the location of the grid and the location
    of the first cell of the grid. Provides methods to get cells at which items
    are present.
    """

    def __init__(self, grid_location: Location, cell_0_0_location: Location,
                 rows, columns,
                 border_x, border_y):
        """
        Args:
            grid_location (Location):
            cell_0_0_location (Location):
            rows:
            columns:
            border_x:
            border_y:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.lf = LocationFactory()
        self.grid = self.lf.get(grid_location)
        self.cell00 = self.lf.get(cell_0_0_location)
        self.rows = rows
        self.cols = columns
        self.border_x = border_x
        self.border_y = border_y

    def get_cells_in_positions(self, positions):
        """Returns cells in the grid for the given positions. :param positions:
        The absolute positions of cells.

        Args:
            positions:

        Returns:
            A list of cells at the given positions.
        """
        return self._get_cells_for_positions(positions)

    def get_cells_not_in_positions(self, positions):
        """
        Args:
            positions:
        """
        cells = self._get_cells_for_positions(positions)
        item_positions = {}
        for i in range(0, self.rows):
            for j in range(0, self.cols):
                if (i, j) not in cells:
                    item_positions[(i, j)] = 1
        return item_positions

    def get_cell_location(self, cell):
        """Returns the bounding location for a given cell.

        Args:
            cell:
        """
        if not self._is_in_bounds(cell):
            return False

        i = cell[0]
        j = cell[1]

        x1 = self.cell00.x1 + j * (self.cell00.get_width() + self.border_x)
        y1 = self.cell00.y1 + i * (self.cell00.get_height() + self.border_y)
        x2 = self.cell00.x2 + j * (self.cell00.get_width() + self.border_x)
        y2 = self.cell00.y2 + i * (self.cell00.get_height() + self.border_y)
        return self.lf.create(x1, y1, x2, y2)

    def _get_cells_for_positions(self, positions):
        """
        Args:
            positions:
        """
        offset_x, offset_y = \
            (self.cell00.x1 - self.grid.x1, self.cell00.y1 - self.grid.y1)
        width = self.cell00.get_width() + 2*self.border_x
        height = self.cell00.get_height() + 2*self.border_y
        ret = [
            (abs(p[1] - offset_y) // height, abs(p[0] - offset_x) // width)
            for p in positions]
        # positions might contain close positions that map to the same cell.
        # This can cause ret to contain duplicate values, so remove duplicates
        # by converting to a set and back.
        return list(set(ret))

    def _is_in_bounds(self, cell):
        """
        Args:
            cell:
        """
        return (cell[0] >= 0 and cell[1] >= 0) and (
                cell[0] < self.rows and cell[1] < self.cols)
