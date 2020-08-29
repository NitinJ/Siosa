import threading
import time
import logging
import queue
from scanf import scanf

from siosa.client.hideout_event import HideoutEvent
from siosa.client.trade_event import TradeEvent
from siosa.client.location_change_event import ZoneChangeEvent

class ClientLogListener(threading.Thread):
    SLEEP_DURATION = 0.05
    MAX_QUEUE_SIZE = 1000

    def __init__(self,
                 group=None,
                 target=None,
                 name=None,
                 args=(),
                 kwargs=None,
                 verbose=None,
                 client_log_file_path="C:\Program Files (x86)\Steam\steamapps\common\Path of Exile\logs\Client.txt"):
        super(ClientLogListener, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.target = target
        self.name = name
        
        self.path = client_log_file_path
        self.last_read_ptr = None

        self.trade_event_queue = queue.Queue(ClientLogListener.MAX_QUEUE_SIZE)
        self.hideout_event_queue = queue.Queue(ClientLogListener.MAX_QUEUE_SIZE)
        self.location_change_event_queue = queue.Queue(ClientLogListener.MAX_QUEUE_SIZE)

        self.filters = self._get_filters()

    def run(self):
        while True:
            for line in self.read_unread_lines():
                for filter in self.filters:
                    filter_output = filter(line)
                    if filter_output['pass']:
                        queue = filter_output['queue']
                        self.logger.debug("Adding queue event for line from client log. {}".format(line))
                        queue.put(filter_output['data'])
            time.sleep(ClientLogListener.SLEEP_DURATION)
        return

    def read_unread_lines(self):
        lines = []
        f = open(self.path, 'r')
        if self.last_read_ptr is not None:
            f.seek(self.last_read_ptr)
        else:
            f.seek(0, 2)

        for line in f.readlines():
            lines.append(line)

        if len(lines):
            self.logger.debug(
                "Got {} new lines from client log.".format(len(lines)))

        self.last_read_ptr = f.tell()
        f.close()
        return lines

    def _get_filters(self):
        return [
            self.trade_event_filter,
            self.hideout_event_filter,
            self.location_change_event_filter
        ]

    def trade_event_filter(self, log_line):
        data = TradeEvent.create(log_line)
        return {
            'pass': (data is not None),
            'data': data,
            'queue': self.trade_event_queue
        }

    def hideout_event_filter(self, log_line):
        data = HideoutEvent.create(log_line)
        return {
            'pass': (data is not None),
            'data': data,
            'queue': self.hideout_event_queue
        }

    def location_change_event_filter(self, log_line):
        data = ZoneChangeEvent.create(log_line)
        return {
            'pass': (data is not None),
            'data': data,
            'queue': self.location_change_event_queue
        }
