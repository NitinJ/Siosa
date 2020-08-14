import time

from siosa.control.game_step import Step
from siosa.data.zones import Zones


class ChangeZone(Step):
    LOCATION_ENTRY_WAIT_TIME = 10
    def __init__(self, game_state, zone):
        Step.__init__(self, game_state)
        self.zone = zone
    
    def execute(self):
        self.logger.info("Executing step: ChangeZone")
        self.cc.console_command("/" + str(self.zone.value))
        success = self._wait_for_zone()
        if not success:
            raise Exception("Cannot travel to zone: {}".format(self.zone))
        self.logger.debug("Moved to zone {}".format(self.zone.value))
        self.game_state.update({'current_zone': Zones.HIDEOUT})

    def _wait_for_zone(self):
        self.logger.debug("Waiting to enter zone: {}".format(self.zone))
        t1 = time.time()
        while True:
            t2 = time.time()
            if t2 - t1 > ChangeZone.LOCATION_ENTRY_WAIT_TIME:
                self.logger.debug("Timed out while waiting to enter zone: {}".format(self.zone))
                return False
            state = self.game_state.get()
            if state['current_zone'] == self.zone:
                return True
            time.sleep(0.05)
