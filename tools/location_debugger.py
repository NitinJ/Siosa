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
        LocationDrawer.draw(location_obj)


if __name__ == "__main__":
    filters = ['INVENTORY', 'STASH']
    for class_attr in dir(Locations):
        if class_attr.startswith("__"):
            continue
        for filter in filters:
            if class_attr.find(filter) >= 0:
                location_obj = getattr(Locations, class_attr)
                show_location(class_attr, location_obj)
