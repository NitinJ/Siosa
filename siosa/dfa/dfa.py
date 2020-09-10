import asyncio
import logging
import threading

from siosa.dfa.dfa_state import DfaState


class Dfa(threading.Thread):
    SLEEP_DURATION = 0.01

    def __init__(self, state: DfaState, end: DfaState):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self.state = state
        self.end = end
        self.old_state_str = None

        self.fn = {}
        self.running_task = None

        self.event_loop = asyncio.new_event_loop()

    def add_state_fn(self, s1: DfaState, transition_fn):
        self.fn[s1.to_string()] = transition_fn

    def run(self):
        self.event_loop.create_task(self.run_ev())
        self.event_loop.run_forever()
        self.event_loop.close()

    async def run_ev(self):
        while True:
            if self.state.equals(self.old_state_str):
                continue
            # State change.
            if self.state.equals(self.end):
                self.logger.debug("End state({}) reached from {}".format(
                    self.old_state_str, self.state))
                break
            if self.old_state_str:
                self.logger.debug("State changed from {} to {}".format(
                                  self.old_state_str,
                                  self.state.to_string()))
            self.old_state_str = self.state.to_string()

            # Stop any running tasks
            if self.running_task and not self.running_task.done():
                self.running_task.cancel()

            new_state_str = self.state.to_string()
            if new_state_str in self.fn:
                self.logger.debug("New state: {}".format(new_state_str))
                fn = self.fn[new_state_str]
                try:
                    self.running_task = \
                        self.event_loop.create_task(fn(), name=new_state_str)
                    self.logger.debug("{}: {}".format(
                        self.running_task.get_name(), self.running_task.done()))
                except:
                    self.logger.debug("Exception in dfa fuck")
            await asyncio.sleep(Dfa.SLEEP_DURATION)
