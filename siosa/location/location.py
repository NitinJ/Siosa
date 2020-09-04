from siosa.location.resolution import Resolution


class Location:
    """
    Any location on screen on a given resolution.
    """

    def __init__(self, x1, y1, x2, y2, resolution: Resolution, name=""):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.resolution = resolution
        self.name = name
