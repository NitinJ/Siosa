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
        name:
    """
    pyautogui.confirm(
        text='Press OK to verify template({}) on location({})'.format(
            template,
            template.template_name),
        title='Grab template',
        buttons=['OK'])
    # tm = ReusableTemplateMatcher(
    #     Locations.TRADE_WINDOW_FULL, debug=True)
    # print(tm.match_template(template))

    tm = TemplateMatcher(template, debug=True, scale=1)
    return tm.match(match_location)
    # tm = TradeWindowCurrencyMatcher(match_in_game_location, debug=True, scale=1.5)
    # print(tm.match_template(template))


if __name__ == "__main__":
    # for i in range(6, 11):
    #     template_info = TemplateRegistry.get_template_for_currency_stack("exalt", i)
    #     verify_template(Template.from_registry(template_info, scale=1.5), Locations.TRADE_WINDOW_OTHER)

    # grid = Grid(Locations.STASH_TAB, Locations.STASH_QUAD_0_0, 24, 24, 2, 2)
    grid = Grid(Locations.STASH_TAB, Locations.STASH_NORMAL_0_0, 12, 12, 2, 2)
    print(grid.get_cell_location((2, 2)))
    template_info = [
        TemplateRegistry.NORMAL_STASH_0_0.get(),
        LocationFactory().get(Locations.STASH_TAB),
    ]
    points = verify_template(*template_info)
    pprint(points)
    cells = grid.get_cells_in_positions(points)
    print("n cells : {}".format(len(cells)))
    pprint(cells)

