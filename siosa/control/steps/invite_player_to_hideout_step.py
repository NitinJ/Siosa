import time

from siosa.control.console_controller import Commands
from siosa.control.game_step import Step


class InvitePlayerToHideoutStep(Step):
    PLAYER_ENTRY_WAIT_TIME = 15

    def __init__(self, player_account_name):
        Step.__init__(self)
        self.player_account_name = player_account_name

    def execute(self, game_state):
        self.game_state = game_state
        self.cc.console_command(
            Commands.INVITE_TO_PARTY(self.player_account_name))
        status = self._wait_for_player_to_join_hideout()
        if not status:
            raise Exception("Timeout while waiting for player to join hideout")

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
            if self.player_account_name in self.game_state.get()[
                'players_in_hideout']:
                return True
            time.sleep(0.01)
