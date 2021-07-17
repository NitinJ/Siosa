import logging
from enum import Enum

from server.services.service_type import ServiceType
from siosa.client.log_listener import ClientLogListener
from siosa.control.game_controller import GameController
from siosa.control.test_task import TestTask
from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.stash import Stash
from siosa.network.poe_api import PoeApi
from siosa.trader.trade_controller import TradeController


class TaskType(Enum):
    TRADE = 'trade'
    STASH_TAB_CLEANER = 'stash_tab_cleaner'
    TEST = 'test'

    @staticmethod
    def from_str(s):
        for enm in list(TaskType):
            if enm.value == s:
                return enm
        return None


class TaskService:
    def __init__(self, config):
        """
        Args:
            config:
        """
        self.type = ServiceType.TASK
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.log_listener = None
        self.game_controller = None
        self.trade_controller = None
        self.running_task_type = None
        self.gc_task = None
        self._init()

    def _init(self):
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
        stash = Stash()

        # Log listener listens on the client log for incoming events like -
        # trades, location change events.
        self.log_listener = ClientLogListener()
        self.log_listener.start()

    def get_task(self):
        t = self.running_task_type
        if t == TaskType.TRADE:
            return {"task": t.value, "state": "running"}
        elif self.gc_task:
            # GC task
            return {"task": t.value, "state": self.gc_task.get_state().value}
        else:
            return {"task": None}

    def create_task(self, task_type):
        try:
            if task_type == TaskType.TRADE:
                self._create_trade_task()
            elif task_type == TaskType.TEST:
                self._create_gc_task(task_type)
            self.running_task_type = task_type
            return True
        except:
            return False

    def _create_trade_task(self):
        self._restart_game_controller()
        self._restart_trade_controller()

    def _create_gc_task(self, task_type):
        self._stop_trade_controller()
        self._restart_game_controller()
        task = None
        if task_type == TaskType.TEST:
            task = TestTask(10)
        self.game_controller.submit_task(task)
        self.gc_task = task

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

    def _restart_game_controller(self):
        self._stop_game_controller()
        try:
            self.game_controller = GameController(self.log_listener)
        except Exception as err:
            self.logger.error("Error creating game_controller : {}".format(err))

    def _restart_trade_controller(self):
        self._stop_trade_controller()
        try:
            self.trade_controller = TradeController(self.game_controller,
                                                    self.log_listener,
                                                    self.config)
            self.trade_controller.start()
        except Exception as err:
            self.logger.error("Error creating game_controller : {}".format(err))
