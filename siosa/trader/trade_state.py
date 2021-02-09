import logging
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
    TRADING_NO_A = ('TRADING', 'NOT_OFFERED', 'ACCEPTED')

    TRADING_O_NO = ('TRADING', 'OFFERED', 'NOT_OFFERED')
    TRADING_O_O = ('TRADING', 'OFFERED', 'OFFERED')
    TRADING_O_A = ('TRADING', 'OFFERED', 'ACCEPTED')

    TRADING_VS_A = ('TRADING', 'VERIFIED_SUCCESS', 'ACCEPTED')
    TRADING_VS_R = ('TRADING', 'VERIFIED_SUCCESS', 'RETRACTED')

    TRADING_VF_R = ('TRADING', 'VERIFIED_FAIL', 'RETRACTED')
    TRADING_VF_A = ('TRADING', 'VERIFIED_FAIL', 'ACCEPTED')

    TRADING_A_R = ('TRADING', 'ACCEPTED', 'RETRACTED')
    TRADING_A_A = ('TRADING', 'ACCEPTED', 'ACCEPTED')

    @staticmethod
    def create_from_trading_state(state_me: str, state_other: str):
        return States.create('TRADING', state_me, state_other)

    @staticmethod
    def create(state_main: str, state_me: str, state_other: str):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        state_tuple = (state_main, state_me, state_other)
        valid_state = States.is_valid_state(state_tuple)
        if valid_state:
            return valid_state

        logger.debug("State is invalid. Cannot create: {}".format(state_tuple))
        return None

    @staticmethod
    def is_valid_state(state):
        """
        Args:
            state: A tuple of (main_state, me_state, other_state)
        Returns:
            Whether the tuple is a valid state or not.
        """
        for s in list(States):
            if s.value == state:
                return s
        return False


class TradeState(DfaState):
    FORMAT = "({}_{}_{})"

    @synchronized
    def update_me(self, me: str):
        main = self.state_obj.value[0]
        other = self.state_obj.value[2]
        return self.update(States.create(main, me, other))

    @synchronized
    def update_other(self, other: str):
        main = self.state_obj.value[0]
        me = self.state_obj.value[1]
        return self.update(States.create(main, me, other))

    @synchronized
    def update_main(self, main: str):
        return self.update(States.create(main, '', ''))

    @synchronized
    def _is_transition_valid(self, to):
        if not isinstance(to, States):
            return False

        (to_main, to_me, to_other) = to.value
        (from_main, from_me, from_other) = self.state_obj.value

        if from_main == 'ENDED':
            return False

        if to_main == 'LEFT':
            # Player can leave anytime.
            return True

        # Both are trading.
        if from_me in ['VERIFIED_SUCCESS', 'VERIFIED_FAIL'] \
                and to_me in ['OFFERED', 'ACCEPTED']:
            # Cannot go from verified success/fail to offered. Can only go to
            # not-offered.
            return False

        if from_main == ['ACCEPTED'] and to_main in ['NOT_STARTED',
                                                     'AWAITING_TRADE',
                                                     'TRADING', 'CANCELLED']:
            # Cannot go from trade accepted to any previous states.
            return False

        if from_main == ['ENDED']:
            # Cannot go from trade ended to anywhere.
            return False

        return True
