import logging
import queue
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
from siosa.data.stash import Stash, StashTab
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_controller import GameController
from siosa.client.log_listener import ClientLogListener
from siosa.image.inventory_scanner import InventoryScanner
from siosa.location.location_factory import Locations

FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
logging.basicConfig(format=FORMAT)


def run():
    config_file_path = os.path.join(os.path.dirname(__file__), "config.json")
    config = SiosaConfig(config_file_path).config
    
    # api = PoeApi(config['account_name'], config['poe_session_id'])
    # exchange = CurrencyExchange(api)
    
    # # stash = Stash()
    # # stash.get_stash_tab_by_name("SELL").get_item_at_location(9, 9)
    # # stash.get_stash_tab_by_name("SELL").get_item_at_location(10, 2)
    
    # log_listener = ClientLogListener()
    # gc = GameController(log_listener)
    
    inventory_scanner = InventoryScanner()
    print(inventory_scanner.scan())

if __name__ == "__main__":
    run()
