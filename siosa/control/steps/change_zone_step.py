import time

from siosa.control.game_step import Step, StepStatus


class ChangeZone(Step):
    LOCATION_ENTRY_WAIT_TIME = 20

    def __init__(self, zone):
        """
        Args:
            zone:
        """
        Step.__init__(self)
        self.zone = zone

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state
        self.cc.console_command("/" + str(self.zone.value))
        success = self._wait_for_zone()

        if not success:
            return StepStatus(False,
                              "Cannot travel to zone: {}".format(self.zone))

        self.logger.debug("Moved to zone {}".format(self.zone.value))
        self.game_state.update({'current_zone': self.zone})
        return StepStatus(True)

    def _wait_for_zone(self):
        self.logger.debug("Waiting to enter zone: {}".format(self.zone))
        t1 = time.time()
        while True:
            t2 = time.time()
            if t2 - t1 > ChangeZone.LOCATION_ENTRY_WAIT_TIME:
                self.logger.debug(
                    "Timed out while waiting to enter zone: {}".format(
                        self.zone))
                return False
            state = self.game_state.get()
            if state['current_zone'] == self.zone:
                return True
            time.sleep(0.05)
