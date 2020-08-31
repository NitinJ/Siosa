import logging
import threading
import time

from siosa.control.game_task_store import GameTaskStore


class GameTaskExecutor(threading.Thread):
    TASK_STATE_CHECK_DELAY = 0.01

    def __init__(self, game_state):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.game_state = game_state
        self.task_store = GameTaskStore()
        self.running_task = None
        self.lock = threading.Lock()

    def submit_task(self, task):
        if not task:
            return
        self.logger.debug(
            "New task submitted to executor: {}".format(task.name))
        self.lock.acquire()
        self.task_store.add(task)
        self.lock.release()

    def run(self):
        while True:
            self.lock.acquire()
            task = self.task_store.get_next()
            self.lock.release()

            if not task:
                continue

            if self.running_task is None:
                self.logger.debug("There is no task running. Executing "\
                    "task: {}".format(task.name))
                self.running_task = task
                task.run_task(self.game_state)
            elif task != self.running_task:
                self.logger.debug("Executing a new task: {}".format(task.name))
                if self.running_task.is_running():
                    self.logger.debug("Pausing currently running task: {}"\
                                      .format(self.running_task.name))
                    self.running_task.pause()

                self.running_task = task
                if task.is_paused():
                    task.resume(self.game_state)
                else:
                    # Not started, so start it.
                    task.run_task(self.game_state)

            time.sleep(GameTaskExecutor.TASK_STATE_CHECK_DELAY)
