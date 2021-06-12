import random


class InGameLocation:
    def __init__(self, x1, y1, x2, y2, name):
        """
        Creates an InGame location, which is always based on the current screen
        resolution.
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.name = name

    def get_random_point(self):
        x = random.randint(self.x1, self.x2)
        y = random.randint(self.y1, self.y2)
        return x, y

    def get_center(self):
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def get_center_location(self):
        """
        Returns an InGameLocation for center of the current location.
        Returns:
            InGameLocation
        """
        x = (self.x1 + self.x2) // 2
        y = (self.y1 + self.y2) // 2
        return InGameLocation(x, y, x, y, self.name)

    def equals(self, other):
        return str(other) == str(self)

    def get_width(self):
        return self.x2 - self.x1

    def get_height(self):
        return self.y2 - self.y1

    def get_scaled_location(self, factor):
        return InGameLocation(
            int(self.x1 * factor),
            int(self.y1 * factor),
            int(self.x2 * factor),
            int(self.y2 * factor),
            self.name)

    def __str__(self):
        return "({}, {}, {}, {})".format(self.x1, self.y1, self.x2, self.y2)
