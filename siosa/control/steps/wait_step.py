import time

from siosa.control.game_step import Step, StepStatus


class Wait(Step):
    def __init__(self, wait_time_in_secs):
        Step.__init__(self)
        self.wait_time_in_secs = wait_time_in_secs

    def execute(self, game_state):
        time.sleep(self.wait_time_in_secs)
        return StepStatus(True)
