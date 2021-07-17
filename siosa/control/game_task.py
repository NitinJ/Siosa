import logging
import threading
import time
from enum import Enum

from siosa.common.decorations import abstractmethod, synchronized
from siosa.control.window_controller import WindowController


class TaskState(Enum):
    NOT_STARTED = 0
    RUNNING = 1
    # Stopped due to an error.
    STOPPED = 2
    # Completed either successfully or unsuccessfully.
    COMPLETE = 3


def _is_valid_state_transition(state_from, state_to):
    """
    Args:
        state_from:
        state_to:
    """
    if state_from == state_to:
        return True
    if state_to == TaskState.NOT_STARTED or state_from == TaskState.COMPLETE:
        return False
    if state_from == TaskState.STOPPED and state_to != TaskState.COMPLETE:
        return False


class Task(threading.Thread):
    """Encapsulates a game task. Game tasks run inside the game and are executed
    via the GameTaskExecutor. A single task is a thread and can have multiple
    reusable components called Steps. Steps of a task are synchronous and are
    ran in a sequence. Child classes of this class must return an iterator of
    steps to be executed and also handle cleanup in case any of the steps fail
    to execute. Tasks cannot be paused but can be stopped. Tasks are stopped
    when Path of Exile is not in focus. In which case tasks must handle cleanup.
    """
    STEP_EXECUTION_DELAY = 0.1

    def __init__(self, priority, name='GameTask'):
        """
        Args:
            priority:
            name:
        """
        threading.Thread.__init__(self, name=name)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.lock = threading.RLock()

        # Game state is provided at task runtime.
        self.game_state = None
        self._last_step_execution_status = None

        # TODO: Move priorities to a different file and incorporate
        #  comparison logic there.
        self.priority = priority

        self.state = TaskState.NOT_STARTED
        self.wc = WindowController()

    def run_task(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state
        return self.start()

    def stop(self):
        self.logger.info("Stopping task: {}".format(self.name))
        self.set_state(TaskState.STOPPED)

    @synchronized
    def set_state(self, state):
        """
        Args:
            state:
        """
        self.state = state
        self._log_task_status()

    @synchronized
    def has_started(self):
        return self.state is not TaskState.NOT_STARTED

    @synchronized
    def is_running(self):
        return self.state is TaskState.RUNNING

    @abstractmethod
    def get_steps(self):
        """Returns: Returns an iterator for the steps of the task."""
        pass

    def _cleanup_internal(self):
        """Runs when a step in the task execution throws an exception. Can be
        overridden by child classes to ensure that game state is cleaned up
        properly. A task cannot be stopped while cleanup is underway.

        Returns: None
        """
        pass

    def _get_last_step_result(self):
        """Returns: Returns the execution status of the last step that was run.
        Child classes can make use of this to evaluate what step to run next.
        """
        return self._last_step_execution_status

    def _log_task_status(self):
        self.logger.info(
            "GameTask: {}, status: {}".format(self.name, self.state))

    def run(self):
        self.set_state(TaskState.RUNNING)
        self.wc.move_to_poe()
        state_old = self.state

        for step in self.get_steps():
            state_new = self.state
            if not _is_valid_state_transition(state_old, state_new):
                self.logger.error(
                    "Invalid state transition from: {}, to: {}".format(
                        state_old, state_new))
                self.set_state(TaskState.STOPPED)
                break

            if state_new in (TaskState.STOPPED, TaskState.COMPLETE):
                break

            if state_new == TaskState.RUNNING:
                try:
                    self.logger.info("Executing step: {}".format(step))
                    self._last_step_execution_status = \
                        step.execute(self.game_state)
                    self.logger.info("Executed step: {}, status: {}".format(
                        step, self._last_step_execution_status))

                    if not self._last_step_execution_status.success:
                        self.logger.error(
                            "Step: {} failed with status: {}".format(
                                step, self._last_step_execution_status.info))

                except Exception as err:
                    self.logger.warning(
                        "Step({}) failed in Task({}) err: {}".format(
                            step, self.name, err), stack_info=True,
                        exc_info=True)
                    self.set_state(TaskState.STOPPED)
                    break
            state_old = state_new
            time.sleep(Task.STEP_EXECUTION_DELAY)

        if self.state == TaskState.STOPPED:
            self.logger.info("GameTask stopped: {}".format(self.name))
            self._cleanup()

        # Mark as complete and return.
        self.set_state(TaskState.COMPLETE)
        self.logger.info("GameTask complete: {}".format(self.name))

    def _cleanup(self):
        self.logger.info(
            "Cleaning up task: {} on state: {}".format(self.name, self.state))
        self._cleanup_internal()
