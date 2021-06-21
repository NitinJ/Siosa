import logging
import time

from siosa.control.game_state import GameState
from siosa.control.game_step import Step, StepStatus
from siosa.control.steps.place_stash_step import PlaceStash
from siosa.control.window_controller import WindowController
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


class OpenStash(Step):
    STASH_OPEN_WAIT_TIME = 2

    def __init__(self):
        Step.__init__(self)
        self.tm = \
            TemplateMatcher(
                Template.from_registry(TemplateRegistry.STASH_BANNER))

    def execute(self, game_state):
        gs = game_state.get()

        # Check if stash already open
        if self.tm.match(self.lf.get(Locations.STASH_BANNER)):
            self.logger.info("Stash already open")
            if not gs['stash_open']:
                game_state.update({'stash_open': True})
            return StepStatus(True)

        points = self.tm.match(self.lf.get(Locations.SCREEN_FULL))
        if points:
            points = points[0]
            self.logger.debug("Stash tab found@ {}".format(points))
            stash_location = self.lf.create(points[0], points[1], points[0],
                                            points[1])
            self.mc.click_at_location(stash_location)
            game_state.update({'stash_open': True})
            game_state.update({
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
        while not self.tm.match(self.lf.get(Locations.STASH_BANNER)):
            if time.time() - ts1 > OpenStash.STASH_OPEN_WAIT_TIME:
                return False
            time.sleep(0.1)
        return True


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT)

    s = OpenStash()
    gs = GameState()

    wc = WindowController()
    wc.move_to_poe()

    print(s.execute(gs))
