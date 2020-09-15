import logging
import threading
from copy import deepcopy

from siosa.common.decorations import abstractmethod, synchronized


class DfaState:
    def __init__(self, value):
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.value = value

    @synchronized
    def get_value(self):
        return deepcopy(self.value)

    @synchronized
    def set_value(self, other):
        if self._is_transition_valid(other):
            self.value = other
        else:
            self.logger.warning("Invalid state transition from {} -> {}"
                                .format(self.to_string(), str(self.value)))

    @synchronized
    def equals(self, other):
        if other is None:
            return False
        if isinstance(other, str):
            return self.to_string() == other
        if not isinstance(other, DfaState):
            return False
        return self.to_string() == other.to_string()

    @abstractmethod
    @synchronized
    def to_string(self):
        pass

    @synchronized
    def _is_transition_valid(self, to):
        return True