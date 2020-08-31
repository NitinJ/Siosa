import time
from siosa.control.game_step import Step

class TestStep(Step):
    def __init__(self):
        Step.__init__(self)

    def execute(self, game_state):
        # Nothing.
        print("TEST TASK DOING STUFF.")
        time.sleep(4)
        pass
