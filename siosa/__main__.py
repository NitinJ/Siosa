import logging
import Queue
import threading
import time
from time import sleep

from pygtail import Pygtail

from siosa.client.log_listener import ClientLogListener
from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.control.game_controller import GameController
from siosa.control.game_state import GameState
from siosa.control.game_state_updater import GameStateUpdater
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.poe_currencies import *
from siosa.data.poe_item_factory import PoeItemFactory
from siosa.data.stash import Stash
from siosa.location.location_factory import LocationFactory, Locations
from siosa.network.poe_api import PoeApi
from siosa.trader.trade_controller import TradeController
from siosa.trader.trade_request import TradeRequest

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)



if __name__ == "__main__":
    # factory = LocationFactory()
    # currency_center = factory.get(Locations.CURRENCY_CENTER)
    # mc = MouseController(factory, 0.2)
    # mc.move_mouse(currency_center)

    # kc = KeyboardController()
    # item_factory = PoeItemFactory()
    api = PoeApi("MopedDriverr", "952f84865d28d000cba67dcb1d044914")
    exchange = CurrencyExchange(api)
    poe_clipboard = PoeClipboard()
    while True:
        time.sleep(1)
        poe_clipboard.read_item_at_cursor()

    
    # log_listener = ClientLogListener(name='log-listener')
    # log_listener.start()

    # game_controller = GameController(log_listener)
    # game_controller.sub
    # game_controller.initialize()

    # trade_controller = TradeController(game_controller, log_listener)
    # trade_controller.start_trading()

    # exalt = Currency.create(CurrencyType.EXALT)
    # print exalt.get_value_in_chaos()
    # print exchange.get_exchange_rate(exalt)

    # stash = Stash(api)
    # stash.get_stash_contents(0)
    # api.get_stash_metadata()
    # api.get_all_trades("https://www.pathofexile.com/trade/search/Harvest/WQgb7Gmum")

    # gs = GameState()
    # gsu = GameStateUpdater(gs)
    # gsu.start()
