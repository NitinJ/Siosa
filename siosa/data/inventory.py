from siosa.location.location_factory import LocationFactory, Locations


class Inventory:
    BORDER = 3
    ROWS = 5
    COLUMNS = 12

    @staticmethod
    def get_location(p):
        """
        Returns the absolute position for a given inventory cell on the screen.
        Args:
            p: The cell location

        Returns:
            Absolute position of the cell center on the screen.
        """
        lf = LocationFactory()
        inventory_0_0 = lf.get(Locations.INVENTORY_0_0)
        size_x = inventory_0_0.get_width() + Inventory.BORDER
        size_y = inventory_0_0.get_height() + Inventory.BORDER
        x, y = inventory_0_0.get_center()

        x2 = x + p[1] * size_x
        y2 = y + p[0] * size_y
        return lf.create(x2, y2, x2, y2)
