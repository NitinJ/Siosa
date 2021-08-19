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

        self.width = self.grid.get_width()
        self.height = self.grid.get_height()
        self.rows = rows
        self.cols = columns
        self.border_x = border_x
        self.border_y = border_y
        self.cell_bounds = self._get_cells_bounds()

    def _get_cells_bounds(self):
        cells = {}
        for i in range(0, self.rows):
            for j in range(0, self.cols):
                w = self.width // self.cols
                h = self.height // self.rows
                cells[(i, j)] = ((j * w, (j + 1) * w), (i * h, (i + 1) * h))
        return cells

    def get_cells_in_positions(self, positions):
        """Returns cells in the grid for the given positions. :param positions:
        The absolute positions of cells.

        Args:
            positions:

        Returns:
            A list of cells at the given positions.
        """
        cells = []
        for p in positions:
            x = p[0]
            y = p[1]
            for cell, bounds in self.cell_bounds.items():
                bounds_x = bounds[0]
                bounds_y = bounds[1]
                if bounds_x[0] <= x <= bounds_x[1] and \
                        bounds_y[0] <= y <= bounds_y[1]:
                    cells.append(cell)
        return cells

    def get_cells_not_in_positions(self, positions):
        """
        Args:
            positions:
        """
        cells = self.get_cells_in_positions(positions)
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

    def _is_in_bounds(self, cell):
        """
        Args:
            cell:
        """
        return (cell[0] >= 0 and cell[1] >= 0) and (
                cell[0] < self.rows and cell[1] < self.cols)
