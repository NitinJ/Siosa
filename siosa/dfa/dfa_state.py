import threading
from copy import deepcopy

from siosa.common.decorations import abstractmethod, synchronized


class DfaState:
    def __init__(self, value):
        self.lock = threading.RLock()
        self.value = value

    @synchronized
    def get_value(self):
        return deepcopy(self.value)

    @synchronized
    def set_value(self, other):
        self.value = other

    @synchronized
    def equals(self, other):
        if other is not None:
            if isinstance(other, str):
                return self.to_string() == other
            return self.to_string() == other.to_string()
        return False

    @abstractmethod
    @synchronized
    def to_string(self):
        pass