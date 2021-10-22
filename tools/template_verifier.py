import logging
from pprint import pprint

import pyautogui

from siosa.image.grid import Grid
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)

lf = LocationFactory()


def verify_template(template, match_location):
    """
    Args:
        template:
        match_location:
    """
    pyautogui.confirm(
        text='Press OK to verify template({}) on location({})'.format(
            template,
            match_location),
        title='Grab template',
        buttons=['OK'])
    tm = TemplateMatcher(template, debug=True)
    return tm.match(lf.get(match_location))


if __name__ == "__main__":
    verify_template(TemplateRegistry.TANE.get(), Locations.SCREEN_FULL)

