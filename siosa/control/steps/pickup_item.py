import time

from siosa.control.game_step import Step
from siosa.control.steps.change_stash_tab_step import ChangeStashTab
from siosa.data.stash_item import StashItem


class PickupItem(Step):
    # TODO: Remove this wait time and have a better mechanism to detect if stash
    # has loaded on screen.
    STASH_LOAD_WAIT_TIME = 1

    def __init__(self, stash_item: StashItem):
        Step.__init__(self)
        self.stash_item = stash_item

    def execute(self, game_state):
        self.game_state = game_state

        ChangeStashTab(self.stash_item.stash_tab.index).execute(game_state)

        # Stash sometimes takes a lot of time to load.
        time.sleep(PickupItem.STASH_LOAD_WAIT_TIME)

        if not self.stash_item.stash_tab.is_item_at_location_ingame(
                self.stash_item.position[0],
                self.stash_item.position[1]):
            raise Exception("Item not present at location !")

        cell = list(self.stash_item.position).copy()
        cell.reverse()
        item_position_xy = self.stash_item.stash_tab.get_cell_location(cell)
        self.mc.move_mouse(item_position_xy)
        self.kc.hold_modifier('Ctrl')
        self.mc.click()
        self.kc.unhold_modifier('Ctrl')
        ChangeStashTab(0).execute(game_state)