import time

import pyautogui

from siosa.image.location_drawer import LocationDrawer
from siosa.location.location_factory import LocationFactory, Locations

lf = LocationFactory()


def show_location(location_name, location_obj):
    """
    Args:
        location_name:
        location_obj:
    """
    text = pyautogui.confirm(
        text='Showing location for: {}'.format(location_name),
        title='Location',
        buttons=['OK', 'Skip'])
    if text == 'OK':
        time.sleep(1)
        LocationDrawer.draw(location_obj)


if __name__ == "__main__":
    show_location('TRADE_WINDOW_FULL', Locations.TRADE_WINDOW_FULL)
