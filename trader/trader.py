from time import sleep
import logging
logging.basicConfig(level=logging.DEBUG)
import threading
import time
import Queue
from pygtail import Pygtail

from location.location_factory import LocationFactory, Locations
from clipboard.poe_clipboard import PoeClipboard
from data.poe_item_factory import PoeItemFactory
from trade_request import TradeRequest
from network.poe_api import PoeApi
from data.stash import Stash
from data.poe_currencies import *
from data.currency_exchange import CurrencyExchange
from client.log_listener import ClientLogListener
from control.game_controller import GameController
from trade_controller import TradeController

if __name__ == "__main__":
    # factory = LocationFactory()
    # currency_center = factory.get(Locations.CURRENCY_CENTER)
    # mc = MouseController(factory, 0.2)
    # mc.move_mouse(currency_center)

    # kc = KeyboardController()
    # item_factory = PoeItemFactory()
    # poe_clipboard = PoeClipboard(kc, item_factory)
    # print poe_clipboard.read_item_at_cursor()

    api = PoeApi("MopedDriverr", "952f84865d28d000cba67dcb1d044914")
    
    exchange = CurrencyExchange(api)
    log_listener = ClientLogListener(name='log-listener')
    game_controller = GameController(log_listener)
    trade_controller = TradeController(game_controller, log_listener)

    trade_controller.start_trading()

    # exalt = Currency.create(CurrencyType.EXALT)
    # print exalt.get_value_in_chaos()
    # print exchange.get_exchange_rate(exalt)

    # stash = Stash(api)
    # stash.get_stash_contents(0)
    # api.get_stash_metadata()
    # api.get_all_trades("https://www.pathofexile.com/trade/search/Harvest/WQgb7Gmum")

    # Thread 2 for currency exchange.
    # Thread 3 for updating stash information. stashes,locations,contents.

    # while True:
    #     if not tradeQueue.empty():
    #         line = tradeQueue.get()
    #         print "Got new lines from queue: "
    #         print line

    #         if line:
    #             print "LINE: " + line
    #             print TradeRequest.create_from(line)

    #         time.sleep(0.05)