import logging
import queue
import threading
import time

from siosa.client.hideout_event import HideoutEvent
from siosa.client.location_change_event import ZoneChangeEvent
from siosa.client.trade_event import TradeEvent
from siosa.client.trade_status_event import TradeStatusEvent


class ClientLogListener(threading.Thread):
    SLEEP_DURATION = 0.05
    MAX_QUEUE_SIZE = 1000

    def __init__(self,
                 config,
                 target=None,
                 name=None):
        super(ClientLogListener, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.target = target
        self.name = name
        self.config = config
        self.last_read_ptr = None

        # TODO: Add support for multiple clients listening to a single queue
        # Currently if a client consumes from a queue, other clients will not
        # get the event. Probably create multiple queues each time a client
        # requests a queue.
        self.trade_event_queue = queue.Queue(ClientLogListener.MAX_QUEUE_SIZE)
        self.hideout_event_queue = queue.Queue(ClientLogListener.MAX_QUEUE_SIZE)
        self.location_change_event_queue = queue.Queue(ClientLogListener.MAX_QUEUE_SIZE)
        self.trade_status_event_queue = queue.Queue(
            ClientLogListener.MAX_QUEUE_SIZE)

        self.filters = [
            self.trade_event_filter,
            self.hideout_event_filter,
            self.location_change_event_filter,
            self.trade_status_event_filter
        ]

    def run(self):
        while True:
            for line in self.read_unread_lines():
                for log_filter in self.filters:
                    filter_output = log_filter(line)
                    if filter_output['pass']:
                        self.logger.debug(
                            "Adding queue event({}) for client log line: {}"
                                .format(log_filter, line))
                        filter_output['queue'].put(filter_output['data'])
            time.sleep(ClientLogListener.SLEEP_DURATION)

    def read_unread_lines(self):
        lines = []
        f = open(self.config.get_client_log_file_path(), 'r', encoding="utf8")
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

    def trade_status_event_filter(self, log_line):
        data = TradeStatusEvent.create(log_line)
        return {
            'pass': (data is not None),
            'data': data,
            'queue': self.trade_status_event_queue
        }

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
