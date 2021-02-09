import logging

import pyautogui

from siosa.image.reusable_template_matcher import ReusableTemplateMatcher
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)

lf = LocationFactory()


def verify_template(template_info):
    template_location = lf.get(template_info[1])
    template = template_info[0]
    pyautogui.confirm(
        text='Press OK to verify template on location({})'.format(
            template_location.name),
        title='Grab template',
        buttons=['OK'])
    # tm = ReusableTemplateMatcher(
    #     Locations.TRADE_WINDOW_FULL, confirm_foreground=True, debug=True)
    # print(tm.match_template(template))
    tm = TemplateMatcher(template, debug=True, confidence=0.6, confirm_foreground=False)
    print(tm.match(template_location))


if __name__ == "__main__":
    template_info = [
        Template.from_registry(TemplateRegistry.TRADE_ACCEPT_GREEN_AURA_ME),
        Locations.TRADE_ACCEPT_GREEN_AURA_ME
    ]
    verify_template(template_info)