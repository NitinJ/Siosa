import logging
import Queue
import threading
import time
from time import sleep
import os

from pygtail import Pygtail

from siosa.clipboard.poe_clipboard import PoeClipboard
from siosa.data.currency_exchange import CurrencyExchange
from siosa.network.poe_api import PoeApi
from siosa.control.steps.scan_inventory_step import ScanInventory
from siosa.control.init_task import InitTask
from siosa.control.game_state import GameState
from siosa.config.siosa_config import SiosaConfig

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def run():
    config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = SiosaConfig(config_file_path).config
    
    api = PoeApi(config['account_name'], config['poe_session_id'])
    exchange = CurrencyExchange(api)
    # poe_clipboard = PoeClipboard()
    # while True:
    #     poe_clipboard.read_item_at_cursor()
    
    # time.sleep(1)
    # step = ScanInventory({})
    # step.execute()


if __name__ == "__main__":
    run()
