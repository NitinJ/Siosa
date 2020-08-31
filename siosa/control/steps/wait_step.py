import time

from siosa.control.game_step import Step


class Wait(Step):
    def __init__(self, wait_time_in_secs):
        Step.__init__(self)
        self.wait_time_in_secs = wait_time_in_secs

    def execute(self, game_state):
        self.logger.info("Executing step: Wait")
        time.sleep(self.wait_time_in_secs)
