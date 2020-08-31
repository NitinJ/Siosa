import logging


def _filter(task):
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


class GameTaskStore:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.tasks = []

    def add(self, t):
        self.logger.debug(
            "Adding new task to task store: {}".format(t.name))
        self.tasks.append(t)
        self._update()
        self.logger.debug("New task priorities: {}".format(self.tasks))

    def get_next(self):
        """Returns the next task to run.
        """
        self._update()
        if self.tasks:
            return self.tasks[0]
        return None

    def _update(self):
        tasks = [task for task in self.tasks if _filter(task)]
        tasks.sort(key=lambda t: t.priority, reverse=True)
        if len(tasks) != len(self.tasks):
            self.logger.debug("Tasks priority changed. Old: {}, New:{}"\
                              .format(self.tasks, tasks))
        self.tasks = tasks
