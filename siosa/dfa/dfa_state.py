import logging
import threading
from copy import deepcopy

from siosa.common.decorations import abstractmethod, synchronized


class DfaState:
    def __init__(self, state_obj):
        """
        Args:
            state_obj: A serializable object to represent internal state.
        """
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.state_obj = state_obj

    @synchronized
    def update(self, new_state_obj):
        if not self._is_transition_valid(new_state_obj):
            self.logger.error("Invalid state transition from {} -> {}"
                              .format(self.get(), new_state_obj))
            return False
        self.logger.error("State transition from {} -> {}"
                          .format(self.get(), new_state_obj))
        self.state_obj = new_state_obj
        return True

    @synchronized
    def equals(self, other):
        if isinstance(other, str):
            return self.get() == other
        if type(other) == type(self.state_obj):
            return str(self.state_obj) == str(other)
        if isinstance(other, DfaState):
            return self.get() == other.get()
        return False

    @synchronized
    def get(self):
        return str(self.state_obj)

    @synchronized
    def _is_transition_valid(self, other):
        return True
