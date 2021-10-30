from cv2 import cv2

from siosa.image.location_drawer import LocationDrawer
from siosa.location.location_factory import Locations, LocationFactory
from siosa.location.resolution import Resolution


def get_location_factory(image_path):
    if not image_path:
        return LocationFactory()
    image = cv2.imread(image_path)
    h, w = image.shape[0:2]
    return LocationFactory(resolution=Resolution(w, h))


if __name__ == "__main__":
    # Can be None to show location on screen.
    image_path = 'images/stash.png'

    # Required to initialize Locations
    lf = get_location_factory(image_path)

    location = Locations.INVENTORY
    LocationDrawer.draw(location, image_path)
