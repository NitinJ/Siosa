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


class Resolutions:
    p1080 = Resolution(1920, 1080)
    p720 = Resolution(1280, 720)
