import logging
from enum import Enum


class TradeInfo:
    """All the information about a trade including state."""

    class Status(Enum):
        # When the object is created. This is the default value.
        NOT_STARTED = 'not_started'
        # Trade request has been sent to the player.
        TRADE_REQUEST_SENT = 'trade_request_sent'
        # Trading is active with trade window open.
        TRADING = 'trading'
        # Trade has been accepted by the player by clicking the 'Accept' button.
        # This means that the trade window is still open.
        TRADE_ACCEPTED = 'trade_accepted'
        # Trade has been rejected by the player and the trade window is not open
        TRADE_REJECTED = 'trade_rejected'
        # Trade is complete. Either accepted or rejected.
        TRADE_COMPLETE = 'trade_complete'
        # Trade is over.
        TERMINATED = 'terminated'

    def __init__(self, trade_request, stash_item):
        self.logger = logging.getLogger(__name__)
        self.trade_request = trade_request
        self.stash_item = stash_item
        self.status = TradeInfo.Status.NOT_STARTED
