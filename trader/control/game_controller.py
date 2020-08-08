class GameController:
    def __init__(self):
        self.mouse_position = None
        self.is_stash_open = False
        self.player_position = None
        self.current_stash_tab = None
        self.inventory = []

    def initialize(self):
        # Move to poe
        # go to tane's lab
        # go to hideout
        # Open stash
        # Organize stash
        # Ready !
        pass

    def _get_is_stash_open(self):
        pass
    
    def _open_stash(self):
        pass

    def _move_currency_in_invent_to_stash(self):
        pass

    def _open_stash_tab(self, tab_index):
        pass

    def _pickup_item_from_stash_tab(self, tab_index, stash_item):
        pass

    def _move_item_to_trade_window(self, inventory_item):
        pass

    def trade_item(self, trade):
        pass