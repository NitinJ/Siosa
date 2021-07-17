import asyncio
import logging
import threading

from siosa.dfa.dfa_state import DfaState


class DfaAsyncio(threading.Thread):
    """A DFA implementation that executes tasks based on state transitions. A
    transition function is called when a given state is reached. States are
    encapsulated in DfaState objects. A state can have only one registered
    transition function. Uses asyncio to fire and forget tasks. Running task is
    cancelled if a new one is to be run.
    """

    SLEEP_DURATION = 0.01

    def __init__(self, state: DfaState, end: DfaState):
        """
        Args:
            state (DfaState):
            end (DfaState):
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.state = state
        self.end = end
        self.old_state_str = None
        self.fn = {}
        self.running_task = None
        self.event_loop = asyncio.new_event_loop()

    def add_state_fn(self, state: DfaState, transition_fn):
        """Registers a transition function for a given state.Overwrites any
        already registered function. :param state: The state on which to execute
        transition function :param transition_fn: The transition function

        Returns: None

        Args:
            state (DfaState):
            transition_fn:
        """
        self.fn[state.to_string()] = transition_fn

    def run(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_until_complete(self.run_ev())
        self.event_loop.stop()

    async def run_ev(self):
        while True:
            await asyncio.sleep(DfaAsyncio.SLEEP_DURATION)

            if self.state.equals(self.old_state_str):
                continue

            # State changed.
            self.logger.debug("State changed from {} to {}".format(
                self.old_state_str, self.state.to_string()))

            if self.state.equals(self.end):
                self.logger.debug("End state({}) reached from {}".format(
                    self.state.to_string(), self.old_state_str))
                if self.running_task:
                    await self.running_task
                self.logger.debug("DFA run event loop ending.")
                return

            # Stop any running task
            self._stop_running_task()
            self.old_state_str = self.state.to_string()

            # Run the fn for the new state if it's available.
            self._runfn()

    def _stop_running_task(self):
        if not self.running_task:
            return

        if not self.running_task.done():
            self.logger.debug(
                "Cancelling fn: {}".format(self.running_task.get_name()))
            self.running_task.cancel()
        else:
            try:
                err = self.running_task.exception()
                if err:
                    self.logger.error(
                        "Task failed with exception: {}".format(err),
                        stack_info=True, exc_info=True)
            except:
                # Task might have already been cancelled.
                pass

    def _runfn(self):
        """Runs the fn for the current state. Returns: None"""
        new_state_str = self.state.to_string()
        if new_state_str not in self.fn:
            return

        self.logger.debug("Running fn for new state: {}".format(new_state_str))
        fn = self.fn[new_state_str]
        try:
            self.running_task = \
                self.event_loop.create_task(fn(), name=new_state_str)
        except Exception as err:
            self.logger.debug("Exception in dfa while executing "
                              "fn for {} : {}".format(new_state_str, err),
                              stack_info=True, exc_info=True)
