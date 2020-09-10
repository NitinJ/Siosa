from siosa.common.decorations import synchronized
from siosa.dfa.dfa_state import DfaState


class TradeState(DfaState):
    def __init__(self, state_value):
        super().__init__(state_value)

    def to_string(self):
        return "{}-{}-{}".format(self.value[0], self.value[1], self.value[2])


class States:
    NOT_STARTED = ('NOT_STARTED', '', '')
    AWAITING_TRADE = ('AWAITING_TRADE', '', '')
    TRADING_NO_NO = ('TRADING', 'NOT_OFFERED', 'NOT_OFFERED')
    ACCEPTED = ('ACCEPTED', '', '')
    CANCELLED = ('CANCELLED', '', '')
