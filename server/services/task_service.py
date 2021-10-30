import logging
from enum import Enum

from server.services.service_type import ServiceType
from siosa.client.log_listener import ClientLogListener
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_controller import GameController
from siosa.control.test_task import TestTask
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.stash import Stash
from siosa.network.poe_api import PoeApi
from siosa.roller.roll_task import RollTask
from siosa.roller.roller_config import RollerConfig
from siosa.stash_cleaner.clean_stash_task import CleanStashTask
from siosa.trader.trade_controller import TradeController


class TaskType(Enum):
    TRADE = 'trade'
    STASH_TAB_CLEANER = 'stash_tab_cleaner'
    TEST = 'test'
    ROLLER = 'roller'

    @staticmethod
    def from_str(s):
        for enm in list(TaskType):
            if enm.value == s:
                return enm
        return None


class TaskService:
    def __init__(self, config: SiosaConfig):
        """
        Args:
            config:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.type = ServiceType.TASK
        self.config = config
        self.initialized = False

        self.log_listener = None
        self.game_controller = None
        self.trade_controller = None
        self.running_task_type = None

        self.gc_task = None

    def _maybe_init(self):
        if not self.config.is_valid() or self.initialized:
            return

        # Initializes most of siosa here.
        # Currency exchange for getting chaos-exalt ratios and creating currency
        # items. Uses PoeApi object. PoeApi is used for fetching stuff using poe
        # web api restful endpoints.
        exchange = CurrencyExchange(
            PoeApi(self.config.get_account_name(),
                   self.config.get_poe_session_id(),
                   self.config.get_league()))

        # Stash object for managing stash, stash-tabs and getting static stash
        # information for the account such as - number of tabs, their contents
        # etc.
        stash = Stash(self.config)

        # Log listener listens on the client log for incoming events like -
        # trades, location change events.
        self.log_listener = ClientLogListener(self.config)
        self.log_listener.start()

        self.initialized = True

    def get_task(self):
        t = self.running_task_type
        if t == TaskType.TRADE:
            return {"task": t.value, "state": 1}
        elif self.gc_task:
            # GC task
            return {"task": t.value, "state": self.gc_task.get_state().value}
        else:
            return {"task": None}

    def create_trade_task(self):
        self._maybe_init()
        self._restart_game_controller()
        self._restart_trade_controller()

        self.running_task_type = TaskType.TRADE
        return True

    def create_stash_cleaner_task(self, stash_index):
        self._maybe_init()
        self._stop_trade_controller()

        task = CleanStashTask(stash_index)
        self.gc_task = task
        self.running_task_type = TaskType.STASH_TAB_CLEANER

        self._restart_game_controller()
        self.game_controller.submit_task(task)
        return True

    def create_test_task(self):
        self._maybe_init()
        self._stop_trade_controller()

        task = TestTask(10, 10)
        self.gc_task = task
        self.running_task_type = TaskType.TEST

        self._restart_game_controller()
        self.game_controller.submit_task(task)
        return True

    def create_roll_task(self, roller_config):
        self._maybe_init()
        self._stop_trade_controller()

        task = RollTask(RollerConfig.create_from_json(roller_config))
        self.gc_task = task
        self.running_task_type = TaskType.ROLLER

        self._restart_game_controller(clean_inventory_on_init=False)
        self.game_controller.submit_task(task)
        return True

    def stop_all_tasks(self):
        self._maybe_init()
        self._stop_trade_controller()
        self._stop_game_controller()
        self.running_task_type = None
        self.gc_task = None
        return True

    def _stop_game_controller(self):
        if self.game_controller:
            self.game_controller.stop()
            del self.game_controller
            self.game_controller = None

    def _stop_trade_controller(self):
        if self.trade_controller:
            self.trade_controller.stop()
            del self.trade_controller
            self.trade_controller = None

    def _restart_game_controller(self, clean_inventory_on_init=True):
        self._stop_game_controller()
        try:
            self.game_controller = \
                GameController(self.log_listener,
                               clean_inventory_on_init=clean_inventory_on_init)
        except Exception as err:
            self.logger.error(
                "Error creating game_controller : {}".format(err))

    def _restart_trade_controller(self):
        self._stop_trade_controller()
        try:
            self.trade_controller = TradeController(self.game_controller,
                                                    self.log_listener,
                                                    self.config)
            self.trade_controller.start()
        except Exception as err:
            self.logger.error(
                "Error creating game_controller : {}".format(err))
