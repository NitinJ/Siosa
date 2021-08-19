from __future__ import annotations

from copy import copy
from fractions import Fraction

from siosa.location.resolution import Resolution


class Location:
    """Any location on screen on a given resolution."""

    def __init__(self, x1, y1, x2, y2, resolution: Resolution):
        """
        Args:
            x1:
            y1:
            x2:
            y2:
            resolution (Resolution):
        """
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.resolution = resolution

    def get_width(self):
        return self.x2 - self.x1

    def get_height(self):
        return self.y2 - self.y1

    def aspect_ratio(self):
        return Fraction(self.get_width(), self.get_height())

    def equals(self, other):
        return str(other) == str(self)

    def __str__(self):
        return "({},{},{},{}) @{}".format(self.x1, self.y1,
                                             self.x2, self.y2, self.resolution)

    def get_center(self):
        return (self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2

    def get_center_location(self):
        """
        Returns an Location for center of the current location.
        :returns: Location
        """
        x = (self.x1 + self.x2) // 2
        y = (self.y1 + self.y2) // 2
        return self.__class__(x, y, x, y, self.resolution)

    def get_scaled_for_resolution(self, resolution):
        if self.resolution.equals(resolution):
            return copy(self)
        w_ratio = resolution.w / self.resolution.w
        h_ratio = resolution.h / self.resolution.h
        return self.__class__(
            int(self.x1 * w_ratio),
            int(self.y1 * h_ratio),
            int(self.x2 * w_ratio),
            int(self.y2 * h_ratio),
            resolution)
