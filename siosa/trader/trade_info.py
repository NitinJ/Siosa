import logging
from enum import Enum


class TradeInfo:
    """All the information about a trade including state."""

    class Status(Enum):
        NOT_STARTED = 'not_started'
        STARTING = 'starting'
        INVITED = 'invited'
        JOINED = 'joined'
        LEFT = 'left'
        TRADING = 'trading'
        TRADE_ACCEPTED = 'trade_accepted'
        TRADE_REJECTED = 'trade_rejected'
        TRADE_COMPLETE = 'trade_complete'
        TERMINATED = 'terminated'

    def __init__(self, trade_request, stash_tab, item):
        self.logger = logging.getLogger(__name__)
        self.trade_request = trade_request
        self.stash_tab = stash_tab
        self.item = item

        self.status = TradeInfo.Status.NOT_STARTED
