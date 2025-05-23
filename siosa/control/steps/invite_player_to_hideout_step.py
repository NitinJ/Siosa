import time
from enum import Enum

from siosa.control.console_controller import Commands
from siosa.control.game_step import Step, StepStatus


class Error(Enum):
    TIMEOUT = 0


class InvitePlayerToHideoutStep(Step):
    PLAYER_ENTRY_WAIT_TIME = 60

    def __init__(self, player_account_name, msg=None):
        """
        Args:
            player_account_name:
            msg:
        """
        Step.__init__(self)
        self.player_account_name = player_account_name
        self.msg = msg

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state
        if self.msg:
            self.cc.send_chat(self.player_account_name, self.msg)
        self.cc.player_console_command(self.player_account_name,
                                       Commands.INVITE_TO_PARTY)
        status = self._wait_for_player_to_join_hideout()
        if not status:
            return StepStatus(False, Error.TIMEOUT)
        return StepStatus(True)

    def _wait_for_player_to_join_hideout(self):
        self.logger.debug("Waiting to {} to enter hideout".format(
            self.player_account_name))
        t1 = time.time()
        while True:
            t2 = time.time()
            if t2 - t1 > InvitePlayerToHideoutStep.PLAYER_ENTRY_WAIT_TIME:
                self.logger.debug("Timed out while waiting for " \
                                  "player({}) to enter hideout".format(
                    self.player_account_name))
                return False
            players_in_hideout = self.game_state.get()['players_in_hideout']
            self.logger.debug("Players in hideout : {}".format(
                players_in_hideout))
            if self.player_account_name in players_in_hideout:
                self.logger.debug("player({}) has entered hideout".format(
                    self.player_account_name))
                return True
            time.sleep(0.1)
