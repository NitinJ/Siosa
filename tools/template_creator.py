import pyautogui

from siosa.image.template import Template
from siosa.location.location_factory import LocationFactory, Locations

lf = LocationFactory()


def grab_template(name, template_location):
    template_location = lf.get(template_location)
    pyautogui.confirm(
        text='Press OK to grab template({}) on location({})'.format(
            name, template_location.name),
        title='Grab template',
        buttons=['OK'])
    Template.create(name, template_location, overwrite=True, debug=True)


if __name__ == "__main__":
    locations = [
        ('INVENTORY_0_0_fake', Locations.INVENTORY_0_0)
    ]
    for location in locations:
        grab_template(location[0], location[1])
