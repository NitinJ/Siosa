import logging
import os

from siosa.client.log_listener import ClientLogListener
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_controller import GameController
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.stash import Stash
from siosa.network.poe_api import PoeApi
from siosa.trader.trade_controller import TradeController

FORMAT = "%(created)f: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def run():
    # Setup common components which will be used for everything.

    # Configuration
    config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = SiosaConfig(config_file_path).config

    # Currency exchange for getting chaos-exalt ratios and creating currency
    # items. Uses PoeApi object. PoeApi is used for fetching stuff using poe
    # web api restful endpoints.
    exchange = CurrencyExchange(
        PoeApi(config['account_name'], config['poe_session_id']))

    # Stash object for managing stash, stash-tabs and getting static stash
    # information for the account such as - number of tabs, their contents etc.
    stash = Stash()

    # Log listener listens on the client log for incoming events like- trades,
    # location change events.
    log_listener = ClientLogListener()
    log_listener.start()

    # Game controller handles everything that happens in-game. Runs and manages
    # tasks,steps in game.
    gc = GameController(log_listener)

    # Submit test task to test out stuff. All testing needs to be done through
    # test task.
    # gc.submit_task(TestTask(15))

    trader = TradeController(gc, log_listener)
    trader.start_trading()


if __name__ == "__main__":
    run()
