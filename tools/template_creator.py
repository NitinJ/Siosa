import pyautogui

from siosa.image.template import Template
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations
from siosa.location.resolution import Resolutions

lf = LocationFactory(resolution=Resolutions.p1080)


def grab_template(name, template_location):
    """
    Args:
        name:
        template_location:
    """
    template_location = lf.get(template_location)
    pyautogui.confirm(
        text='Press OK to grab template({}) on location({})'.format(
            name, template_location),
        title='Grab template',
        buttons=['OK'])
    TemplateRegistry.create(name, template_location, overwrite=True, debug=True)


if __name__ == "__main__":
    # locations = [
    #     ('INVENTORY_0_0', lf.get(Locations.INVENTORY_0_0))
    # ]
    # for location in locations:
    #     grab_template(location[0], location[1])
    TemplateRegistry.create_from_file(
        "TANE", "C:\\Users\\322\\Desktop\\Path of exile\\tane.png", overwrite=True)
