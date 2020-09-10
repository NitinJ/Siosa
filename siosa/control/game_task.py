import logging
import threading
import time
from enum import Enum

from siosa.common.decorations import abstractmethod, synchronized
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
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.lock = threading.RLock()

        # Game state is provided at task runtime.
        self.game_state = None

        self.steps = steps
        self.step_index = 0

        # TODO: Move priorities to a different file and encorporate
        #  comparison logic there.
        self.priority = priority

        self.state = TaskState.NOT_STARTED
        self.wc = WindowController()

    def get_steps(self):
        return self.steps

    def run_task(self, game_state):
        self.game_state = game_state
        return self.start()

    @synchronized
    def set_state(self, state):
        self.state = state

    def run(self):
        self.wc.move_to_poe()

        self.logger.info("Running GameTask: {}".format(self.name))
        self.set_state(TaskState.RUNNING)
        state_old = self.state
        while True:
            state_now = self.state
            if state_now != state_old:
                self._handle_state_change(state_old, state_now)

            if state_now == TaskState.RUNNING:
                try:
                    self._execute()
                except Exception as err:
                    self.logger.warning("Task failed !: {}: {}".format(
                        self.name, err))
                    self.set_state(TaskState.COMPLETE)
            if state_now == TaskState.STOPPED:
                self.logger.info("GameTask stopped: {}".format(self.name))
                break
            if state_now == TaskState.COMPLETE:
                self.logger.info("GameTask complete: {}".format(self.name))
                break
            state_old = state_now
            time.sleep(0.05)

    def _handle_state_change(self, old, new):
        if old == new:
            return

        if old == TaskState.RUNNING and new in (
                TaskState.PAUSED, TaskState.STOPPED):
            self._cleanup()
        elif old == TaskState.RUNNING and new == TaskState.NOT_STARTED:
            self.logger.error(
                "Task state shifted from {} to {}".format(old, new))
        elif old == TaskState.STOPPED:
            self.logger.error("Task state transition from STOPPED")

    def _cleanup(self):
        self.logger.info(
            "Cleaning up task: {} on state: {}".format(self.name, self.state))
        self._cleanup_internal()
        pass

    @synchronized
    def resume(self, game_state):
        self.game_state = game_state
        self.set_state(TaskState.RUNNING)
        self.logger.info("Resuming task: {}".format(self.name))
        self._resume_internal()

    @synchronized
    def is_paused(self):
        return self.state is TaskState.PAUSED

    def pause(self):
        self.logger.info("Pausing task: {}".format(self.name))
        self.set_state(TaskState.PAUSED)

    @synchronized
    def has_started(self):
        return self.state is not TaskState.NOT_STARTED

    @synchronized
    def is_running(self):
        return self.state is TaskState.RUNNING

    def stop(self):
        self.logger.info("Stopping task: {}".format(self.name))
        self.set_state(TaskState.STOPPED)

    # Executes 1 step.
    def _execute(self):
        self.lock.acquire()

        if self.step_index >= len(self.steps):
            self.state = TaskState.COMPLETE
            self.lock.release()
            return

        time.sleep(Task.STEP_EXECUTION_DELAY)
        try:
            self.steps[self.step_index].execute(self.game_state)
            self.logger.warning("Executed step: {}".format(
                self.steps[self.step_index]))
        except Exception as err:
            self.logger.warning("Task failed !: {}: {}".format(
                self.name, err))
            self.set_state(TaskState.STOPPED)
            self.lock.release()
            return

        self.step_index = self.step_index + 1

        if not self.wc.is_poe_in_foreground():
            self.state = TaskState.PAUSED
            self.lock.release()
            return

        self.lock.release()

    @abstractmethod
    def _resume_internal(self):
        pass

    @abstractmethod
    def _cleanup_internal(self):
        pass
