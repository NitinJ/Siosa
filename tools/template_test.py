import logging
import time

import pyautogui

from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s "
handlers = {
    logging.FileHandler('test.log', encoding='utf-8'),
    logging.StreamHandler()
}
logging.basicConfig(level=logging.INFO, format=FORMAT, handlers=handlers)

lf = LocationFactory()


def verify_template(template, match_location):
    """
    Args:
        template:
        match_location:
        msg:
    """
    tm = TemplateMatcher(template, debug=True)
    return tm.match(lf.get(match_location))


if __name__ == "__main__":
    msg = "1. Goto hideout, where stash, guild-stash & tane are clearly visible"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.STASH.get(), Locations.SCREEN_FULL)
    verify_template(TemplateRegistry.GUILD_STASH.get(), Locations.SCREEN_FULL)
    verify_template(TemplateRegistry.TANE.get(), Locations.SCREEN_FULL)

    msg = "1. Open stash. 2. Inventory should be empty"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.INVENTORY_0_0.get(), Locations.SCREEN_FULL)
    verify_template(TemplateRegistry.STASH_BANNER.get(), Locations.SCREEN_FULL)
    verify_template(TemplateRegistry.INVENTORY_BANNER.get(), Locations.SCREEN_FULL)

    msg = "1. Wait for party notification (left the party)"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.PARTY_NOTIFICATIONS_CLOSE_BUTTON.get(), Locations.SCREEN_FULL)

    msg = "1. Start trade with someone and wait for awaiting trade window"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.AWAITING_TRADE_CANCEL_BUTTON.get(), Locations.SCREEN_FULL)

    msg = "1. Start trade with someone and open trade window"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.TRADE_WINDOW_OTHER_SMALL_0_0.get(), Locations.SCREEN_FULL)
    verify_template(TemplateRegistry.TRADE_WINDOW_ME_EMPTY_TEXT.get(),
                    Locations.SCREEN_FULL)
    verify_template(TemplateRegistry.CANCEL_TRADE_ACCEPT_BUTTON.get(),
                    Locations.SCREEN_FULL)
    verify_template(TemplateRegistry.TRADE_WINDOW_CLOSE_BUTTON.get(),
                    Locations.SCREEN_FULL)

    msg = "1. Wait for other player to accept. Don't accept yet"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.TRADE_ACCEPT_GREEN_AURA.get(), Locations.SCREEN_FULL)

    msg = "1. Hover over all trade items and wait for other player to remove one item"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.TRADE_ACCEPT_RETRACTED.get(), Locations.SCREEN_FULL)

    msg = "1. Close all windows. Stand in hideout"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.DECORATIONS_UTILITIES_ARROW.get(), Locations.SCREEN_FULL)

    msg = "1. OPen the edit hideout small window."
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.DECORATIONS_EDIT_BUTTON.get(), Locations.SCREEN_FULL)

    msg = "1. Click on edit button"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.EDITING_BANNER.get(), Locations.SCREEN_FULL)

    msg = "1. Open stash and go to a NORMAL stash tab (preferably empty)"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.NORMAL_STASH_0_0.get(), Locations.SCREEN_FULL)

    msg = "1. Right click a stash item to open the pricing window"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.PRICE_ITEM_WINDOW_ARROW.get(), Locations.SCREEN_FULL)

    msg = "1. Open stash and go to a QUAD stash tab (preferably empty)"
    pyautogui.confirm(text=msg, title='Grab screenshot', buttons=['OK'])
    time.sleep(0.5)
    verify_template(TemplateRegistry.QUAD_STASH_0_0.get(), Locations.SCREEN_FULL)
