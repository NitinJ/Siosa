import logging
import threading
import time

from siosa.common.decorations import override
from siosa.common.stoppable_thread import StoppableThread
from siosa.control.game_task import Task
from siosa.control.game_task_store import GameTaskStore


class GameTaskExecutor(StoppableThread):
    TASK_STATE_CHECK_DELAY = 0.01

    def __init__(self, game_state):
        """
        Args:
            game_state:
        """
        StoppableThread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.game_state = game_state
        self.task_store = GameTaskStore()
        self.running_task: Task = None
        self.stopping = False
        self.lock = threading.Lock()

    def submit_task(self, task):
        if not task:
            return
        self.logger.debug(
            "New task submitted to executor: {}".format(task.name))
        self.lock.acquire()
        self.task_store.add(task)
        self.lock.release()

    def stop_all_tasks(self):
        if self.running_task and self.running_task.is_alive():
            # If we are already stopping and stop_all_tasks is called again,
            # terminate instead.
            self.running_task.terminate()
        self.task_store.remove_all()

    @override
    def run_once(self):
        time.sleep(GameTaskExecutor.TASK_STATE_CHECK_DELAY)

        self.lock.acquire()
        task = self.task_store.get_next()
        self.lock.release()
        if not task:
            return

        if self.running_task is None:
            self.logger.debug("There is no task running. Executing " \
                              "task: {}".format(task.name))
            self.running_task = task
            task.run_task(self.game_state)
        elif task != self.running_task:
            if self.running_task.is_running():
                self.logger.debug("Stopping currently running task: {}" \
                                  .format(self.running_task.name))
                self.running_task.stop()
            elif not self.running_task.is_alive():
                # We need to check alive status here as task might take some
                # time to stop and during this phase (running -> stopping), the
                # is_running method will return False.
                # TODO: Fix this in GameTask by adding more states like stopping
                # Running task stopped.
                self.running_task = task
                self.logger.debug("Executing a new task: {}".format(task.name))
                task.run_task(self.game_state)