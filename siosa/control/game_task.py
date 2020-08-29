import logging
import threading
import time
from enum import Enum

from siosa.common.decorations import abstractmethod
from siosa.control.window_controller import WindowController


class TaskState(Enum):
    NOT_STARTED = 0
    RUNNING = 1
    PAUSED = 2
    STOPPED = 3
    COMPLETE = 4

class Task(threading.Thread):
    STEP_EXECUTION_DELAY = 0.1
    def __init__(self, priority, steps, name='GameTask'):
        threading.Thread.__init__(self, name=name)
        self.logger = logging.getLogger(__name__)
        
        # Game state is provided at task runtime.
        self.game_state = None
        
        self.steps = steps
        self.step_index = 0
        
        # TODO: Move priorities to a different file and encorporate comparison
        # logic there.
        self.priority = priority
        
        self.state = TaskState.NOT_STARTED
        self.wc = WindowController()
    
    def get_steps(self):
        return self.steps
    
    def run_task(self, game_state):
        self.game_state = game_state
        return self.start()

    def run(self):
        self.logger.info("Running GameTask: {}".format(self.name))
        self.state = TaskState.RUNNING
        state_old = self.state
        while True:
            state_now = self.state
            if state_now != state_old:
                self._handle_state_change(state_old, state_now)
                
            if state_now == TaskState.RUNNING:
                self._execute()
            if state_now == TaskState.STOPPED:
                self.logger.info("GameTask stopped: {}".format(self.name))
                self.cleanup()
                break
            if state_now == TaskState.COMPLETE:
                self.logger.info("GameTask complete: {}".format(self.name))
                self.cleanup()
                break
            state_old = state_now
            time.sleep(0.05)
    
    def _handle_state_change(self, old, new):
        if old == new:
            return
        if old == TaskState.RUNNING and new in (TaskState.PAUSED, TaskState.STOPPED):
            self.cleanup()
        elif old == TaskState.RUNNING and new == TaskState.NOT_STARTED:
            self.logger.warning("Task state shifted from {} to {}".format(old, new))
        elif old == TaskState.PAUSED and new == TaskState.RUNNING:
            self.resume()
        elif old == TaskState.STOPPED:
            self.logger.warning("Task state transition from STOPPED")

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def resume(self, game_state):
        pass

    def is_paused(self):
        return self.state is TaskState.PAUSED
    
    def has_started(self):
        return self.state is not TaskState.NOT_STARTED
        
    def pause(self):
        self.state = TaskState.PAUSED

    def stop(self):
        self.state = TaskState.STOPPED

    # Executes 1 step.
    def _execute(self):
        if self.step_index >= len(self.steps):
            self.state = TaskState.COMPLETE
            return
        time.sleep(Task.STEP_EXECUTION_DELAY)
        self.steps[self.step_index].execute(self.game_state)
        self.step_index = self.step_index + 1
        if not self.wc.is_poe_in_foreground():
            self.state = TaskState.PAUSED
            return