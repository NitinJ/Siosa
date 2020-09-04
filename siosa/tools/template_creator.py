import pyautogui

from siosa.image.template import Template
from siosa.location.location_factory import LocationFactory, Locations

pyautogui.confirm(text='', title='', buttons=['Grab template'])
lf = LocationFactory()
Template.create("INVENTORY_0_0", lf.get(Locations.INVENTORY_0_0),
                overwrite=True)
pyautogui.confirm(text='', title='', buttons=['Grab template'])
Template.create("NORMAL_STASH_0_0", lf.get(Locations.NORMAL_STASH_0_0),
                overwrite=True)
pyautogui.confirm(text='', title='', buttons=['Grab template'])
Template.create("QUAD_STASH_0_0", lf.get(Locations.QUAD_STASH_0_0),
                overwrite=True)