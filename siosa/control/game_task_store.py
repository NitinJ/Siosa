import logging


class GameTaskStore:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.tasks = []

    def add(self, t):
        self.tasks.append(t)
        self._update()

    def get_next(self):
        """Returns the next task to run.
        """
        self._update()
        if self.tasks:
            return self.tasks[0]
        return None

    def _update(self):
        self.tasks = [task for task in self.tasks if self._filter(task)]
        self.tasks.sort(key=lambda t: t.priority, reverse=True)

    def _filter(self, task):
        """Filters tasks. Keeping tasks -
        1. Are not none, and
        2. Have not started or are alive if they have been started.
        Null tasks and tasks that have finished running are filtered out.

        Args:
            task (GameTask): The game task to filter

        Returns:
            Boolean: Whether task is filtered or not. False if filtered. 
        """
        return task and (not task.has_started() or task.is_alive())
