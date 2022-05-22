import logging
import os

from siosa.client.log_listener import ClientLogListener
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_controller import GameController
from siosa.control.game_state import GameState
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.stash import Stash
from siosa.location.location_factory import LocationFactory
from siosa.network.poe_api import PoeApi
from siosa.roller.roll_task import RollTask
from siosa.roller.roller_config import RollerConfig
from siosa.stash_cleaner.clean_stash_task import CleanStashTask
from siosa.trader.trade_controller import TradeController
from siosa.trader.trade_info import TradeInfo
from siosa.trader.trade_state import TradeState, States
from siosa.trader.trade_state_updater import TradeStateUpdater

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    handlers={
        logging.FileHandler('siosa.log', encoding='utf-8'),
        logging.StreamHandler()
    }
)


def run():
    # Setup common components which will be used for everything.
    LocationFactory()

    # Configuration
    config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = SiosaConfig.create_from_file(config_file_path)

    # Currency exchange for getting chaos-exalt ratios and creating currency
    # items. Uses PoeApi object. PoeApi is used for fetching stuff using poe
    # web api restful endpoints.
    exchange = CurrencyExchange(PoeApi(config.get_account_name(),
                                       config.get_poe_session_id(),
                                       config.get_league()))

    # Stash object for managing stash, stash-tabs and getting static stash
    # information for the account such as - number of tabs, their contents etc.
    stash = Stash(config)

    # Log listener listens on the client log for incoming events like- trades,
    # location change events.
    log_listener = ClientLogListener(config)
    log_listener.start()

    # Game controller handles everything that happens in-game. Runs and manages
    # tasks,steps in game.
    gc = GameController(log_listener, clean_inventory_on_init=False)

    # run_roller(gc)
    run_trader(gc, log_listener, config)
    # run_stash_cleaner(gc, 6)
    #
    # game_state = GameState()
    # game_state.update({'players_in_hideout': ['asifwitchexp']})
    # trade_state = TradeState(States.NOT_STARTED)
    # trade_info = TradeInfo()
    # trade_state_updater = TradeStateUpdater(game_state, trade_state, trade_info, log_listener)


def run_stash_cleaner(gc, index):
    gc.submit_task(CleanStashTask(index))


def run_trader(gc, log_listener, config):
    trader = TradeController(gc, log_listener, config)
    trader.start()


def run_roller(gc):
    gc.submit_task(RollTask(
        RollerConfig.create_from_file('roller/config.json')))


if __name__ == "__main__":
    run()
