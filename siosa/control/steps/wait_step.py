import time

from control.game_step import Step

class Wait(Step):
    def __init__(self, game_state, wait_time_in_secs):
        Step.__init__(self, game_state)
        self.wait_time_in_secs = wait_time_in_secs
    
    def execute(self):
        self.logger.info("Executing step: Wait")
        time.sleep(self.wait_time_in_secs)
