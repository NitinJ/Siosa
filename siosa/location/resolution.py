class Resolution:
    def __init__(self, w, h):
        """
        Args:
            w:
            h:
        """
        self.w = w
        self.h = h

    def __str__(self):
        return "{}x{}".format(self.w, self.h)


class Resolutions:
    p1080 = Resolution(1920, 1080)
    p720 = Resolution(1280, 720)
