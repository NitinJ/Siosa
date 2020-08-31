import logging
import os

from siosa.client.log_listener import ClientLogListener
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_controller import GameController
from siosa.control.test_task import TestTask
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.stash import Stash
from siosa.network.poe_api import PoeApi

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def run():
    # time.sleep(2)
    config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = SiosaConfig(config_file_path).config

    api = PoeApi(config['account_name'], config['poe_session_id'])

    exchange = CurrencyExchange(api)
    stash = Stash()

    log_listener = ClientLogListener()
    log_listener.start()

    gc = GameController(log_listener)
    
    # Submit test task to test out stuff. All testing needs to be done through
    # test task.
    gc.submit_task(TestTask())


if __name__ == "__main__":
    run()
