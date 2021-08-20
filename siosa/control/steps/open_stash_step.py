import logging
import os
import time

from siosa.common.util import parent
from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_state import GameState
from siosa.control.game_step import Step, StepStatus
from siosa.control.steps.locate_stash_step import LocateStashStep
from siosa.control.steps.place_stash_step import PlaceStash
from siosa.control.steps.utils import exit_edit_hideout_mode
from siosa.control.window_controller import WindowController
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


class OpenStash(Step):
    STASH_OPEN_WAIT_TIME = 5

    def __init__(self):
        Step.__init__(self)
        self.stash_banner_tm = \
            TemplateMatcher(TemplateRegistry.STASH_BANNER.get())

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        gs = game_state.get()

        # Check if stash already open.
        if self.stash_banner_tm.match_exists(self.lf.get(Locations.STASH_PANE)):
            self.logger.info("Stash already open")
            if not gs['stash_open']:
                game_state.update({'stash_open': True})
            return StepStatus(True)

        result = LocateStashStep().execute(game_state)
        exit_edit_hideout_mode(self.lf, self.mc)

        if result.success:
            gs = game_state.get()
            self.logger.debug("Stash tab found!. Opening")
            self.mc.click_at_location(gs['stash_location'])
            # Stash might take some time to open.
            if self._wait_for_stash_to_open():
                # Stash open.
                game_state.update({
                    'stash_open': True,
                    'stash_location': self.lf.get(Locations.SCREEN_CENTER)
                })
                return StepStatus(True)

        self.logger.debug("Stash tab not found!. Trying center of screen.")
        self.mc.click_at_location(self.lf.get(Locations.SCREEN_CENTER))
        # Stash might take some time to open.
        if self._wait_for_stash_to_open():
            # Stash open.
            game_state.update({
                'stash_open': True,
                'stash_location': self.lf.get(Locations.SCREEN_CENTER)
            })
            return StepStatus(True)

        self.logger.debug("Stash tab not found!. Placing stash tab.")
        PlaceStash().execute(game_state)

        # Stash might take some time to open.
        if self._wait_for_stash_to_open():
            # Stash open.
            game_state.update({
                'stash_open': True,
                'stash_location': self.lf.get(Locations.SCREEN_CENTER)
            })
            return StepStatus(True)
        return StepStatus(False)

    def _wait_for_stash_to_open(self):
        ts1 = time.time()
        while not self.stash_banner_tm.match(self.lf.get(Locations.STASH_PANE)):
            if time.time() - ts1 > OpenStash.STASH_OPEN_WAIT_TIME:
                return False
            time.sleep(0.1)
        return True


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    config_file_path = os.path.join(parent(parent(parent(__file__))),
                                    "config.json")
    print(config_file_path)
    config = SiosaConfig.create_from_file(config_file_path)
    s = OpenStash()
    gs = GameState()

    wc = WindowController()
    wc.move_to_poe()

    print(s.execute(gs))
