import logging
import threading

from siosa.common.decorations import abstractmethod


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self._stop_event = threading.Event()

    def stop(self):
        self.logger.info("Stopping thread : {}".format(self.__class__))
        self._stop_event.set()

    def join(self, *args, **kwargs):
        self.stop()
        super(StoppableThread,self).join(*args, **kwargs)

    def run(self):
        self.logger.info("Starting thread : {}".format(self.__class__))
        while not self._stop_event.is_set():
            self.run_once()

    @abstractmethod
    def run_once(self):
        raise NotImplementedError()