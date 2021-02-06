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
        self.event_loop.run_until_complete(self.run_ev())
        self.event_loop.stop()

    async def run_ev(self):
        while True:
            if self.state.equals(self.old_state_str):
                continue

            # State changed.
            self.logger.debug("State changed from {} to {}".format(
                self.old_state_str,
                self.state.to_string()))
            self.old_state_str = self.state.to_string()

            # Stop any running task
            self._stop_running_task()

            # Run the fn for the new state if it's available.
            self._run_fn_for_current_state()

            if self.state.equals(self.end):
                self.logger.debug("End state({}) reached from {}".format(
                    self.state.to_string(), self.old_state_str))
                if self.running_task:
                    await self.running_task
                return

            await asyncio.sleep(Dfa.SLEEP_DURATION)

    def _stop_running_task(self):
        if self.running_task and not self.running_task.done():
            self.logger.debug(
                "Cancelling fn: {}".format(self.running_task.get_name()))
            self.running_task.cancel()

    def _run_fn_for_current_state(self):
        new_state_str = self.state.to_string()

        if new_state_str in self.fn:
            self.logger.debug(
                "Running fn for new state: {}".format(new_state_str))
            fn = self.fn[new_state_str]
            try:
                self.running_task = \
                    self.event_loop.create_task(fn(),
                                                name=new_state_str)
            except Exception as err:
                self.logger.warning("Exception in dfa while executing "
                                    "fn for {} : {}".format(
                    new_state_str, err), stack_info=True, exc_info=True)