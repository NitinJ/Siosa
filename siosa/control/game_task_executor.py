import threading


class GameTaskExecutor(threading.Thread):
    TASK_STATE_CHECK_DELAY = 0.01

    def __init__(self, game_state):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.game_state = game_state
        self.running_task = None
        self.not_running_tasks = []
        self.lock = threading.Lock()

    def submit_task(self, task):
        self.logger.debug("New task submitted: {}".format(task.name))
        self.lock.acquire()
        self.not_running_tasks.append(task)
        self.lock.release()

    def run(self):
        while True:
            self._update_tasks()
            task = self._get_task_to_run()
            if task:
                u
                    

    def _update_tasks(self):
        """Updates the internal running and not_running tasks

        Returns:
            [type]: [description]
        """
        if self.running_task:
            if self.running_task.is_alive():
                if self.running_task.is_paused():
                    self.not_running_tasks.append(self.running_task)
                    self.running_task = None
            else:
                self.running_task = None
        
        def __filter(task):
            # Filters all tasks which are none or aren't alive
            if not task:
                return False
            # Either not started or alive if started.
            return not task.has_started() or task.is_alive()
                    
        self.not_running_tasks = [task for task in self.not_running_tasks if __filter(task)]
    
    def _get_task_to_run(self):
        tasks = self.not_running_tasks
        if self.running_task:
            tasks.append(self.running_task)
        if not tasks:
            return None
        tasks.sort(key=lambda t: t.priority)
        return tasks[0]

    def _select_task_to_run(self):
        task_with_max_priority = {
            'priority': 0,
            'task': None
        }
        for i in range(0, len(self.not_running_tasks)):
            _task = self.not_running_tasks[i]
            if _task.priority > task_with_max_priority['priority']:
                task_with_max_priority = {
                    'priority': _task.priority,
                    'task': _task
                }
        self.running_task = task_with_max_priority['task']
        self.running_task.run_task(self.game_state)
        return
