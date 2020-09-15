from enum import Enum

from siosa.common.decorations import synchronized
from siosa.dfa.dfa_state import DfaState


class States(Enum):
    # Main states
    NOT_STARTED = ('NOT_STARTED', '', '')
    AWAITING_TRADE = ('AWAITING_TRADE', '', '')
    ACCEPTED = ('ACCEPTED', '', '')
    CANCELLED = ('CANCELLED', '', '')
    LEFT = ('LEFT', '', '')
    ENDED = ('ENDED', '', '')

    # Trading
    TRADING_NO_NO = ('TRADING', 'NOT_OFFERED', 'NOT_OFFERED')
    TRADING_NO_O = ('TRADING', 'NOT_OFFERED', 'OFFERED')
    TRADING_NO_R = ('TRADING', 'NOT_OFFERED', 'RETRACTED')
    TRADING_NO_A = ('TRADING', 'NOT_OFFERED', 'ACCEPTED')

    TRADING_O_NO = ('TRADING', 'OFFERED', 'NOT_OFFERED')
    TRADING_O_O = ('TRADING', 'OFFERED', 'OFFERED')
    TRADING_O_R = ('TRADING', 'OFFERED', 'RETRACTED')
    TRADING_O_A = ('TRADING', 'OFFERED', 'ACCEPTED')

    TRADING_VS_NO = ('TRADING', 'VERIFIED_SUCCESS', 'NOT_OFFERED')
    TRADING_VS_O = ('TRADING', 'VERIFIED_SUCCESS', 'OFFERED')
    TRADING_VS_R = ('TRADING', 'VERIFIED_SUCCESS', 'RETRACTED')
    TRADING_VS_A = ('TRADING', 'VERIFIED_SUCCESS', 'ACCEPTED')

    TRADING_VF_NO = ('TRADING', 'VERIFIED_FAIL', 'NOT_OFFERED')
    TRADING_VF_O = ('TRADING', 'VERIFIED_FAIL', 'OFFERED')
    TRADING_VF_R = ('TRADING', 'VERIFIED_FAIL', 'RETRACTED')
    TRADING_VF_A = ('TRADING', 'VERIFIED_FAIL', 'ACCEPTED')

    TRADING_A_NO = ('TRADING', 'ACCEPTED', 'NOT_OFFERED')
    TRADING_A_O = ('TRADING', 'ACCEPTED', 'OFFERED')
    TRADING_A_R = ('TRADING', 'ACCEPTED', 'RETRACTED')
    TRADING_A_A = ('TRADING', 'ACCEPTED', 'ACCEPTED')

    @staticmethod
    def create_from_trading_state(state_me: str, state_other: str):
        state = ('TRADING', state_me, state_other)
        for s in list(States):
            if s.value == state:
                return s
        return None


class TradeState(DfaState):
    STR_FORMAT = "({}_{}_{})"

    def __init__(self, state_value: States):
        super().__init__(state_value)

    @synchronized
    def to_string(self):
        return TradeState.STR_FORMAT.format(self.value.value[0],
                                            self.value.value[1],
                                            self.value.value[2])

    @synchronized
    def equals(self, other):
        if isinstance(other, States):
            return self.to_string() == TradeState.STR_FORMAT.format(
                *other.value)
        return super().equals(other)

    @synchronized
    def set_state_me_str(self, state_me: str):
        self.value = States.create_from_trading_state(
            state_me, self.value.value[2])

    @synchronized
    def _is_transition_valid(self, to: States):
        if not self.value.value[0] == 'TRADING' or \
                not to.value[0] == 'TRADING':
            return True
        # Both are trading.
        if self.value.value[1] in ['VERIFIED_SUCCESS', 'VERIFIED_FAIL'] \
                and to.value[1] == 'OFFERED':
            # Cannot go from verified success/fail to offered. Can only go to
            # not-offered.
            return False
        return True
