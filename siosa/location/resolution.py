from enum import Enum
from fractions import Fraction


class Resolution:
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def aspect_ratio(self):
        return Fraction(self.w, self.h)

    def __str__(self):
        return "{}x{}".format(self.w, self.h)

    def equals(self, other):
        return other.w == self.w and other.h == self.h

    def get_base_resolution(self):
        """
        Returns: The base supported resolution for this resolution. Base
        resolution is one which has the same aspect ratio among supported
        resolutions.
        """
        for res in Resolutions:
            if res.value.aspect_ratio() == self.aspect_ratio():
                return res.value
        return None


class Resolutions(Enum):
    """
    Supported base resolutions. Resolutions with the same aspect ratio are
    supported
    """
    p1080 = Resolution(1920, 1080)
    ultrawide = Resolution(3440, 1440)
