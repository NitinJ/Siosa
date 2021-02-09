import logging
import time

from siosa.control.game_state import GameState
from siosa.control.game_step import Step
from siosa.control.steps.place_stash_step import PlaceStash
from siosa.control.window_controller import WindowController
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations, LocationFactory


class OpenStash(Step):
    def execute(self, game_state):
        self.logger.info("Executing step: OpenStash")
        gs = game_state.get()
        stash_location = gs['stash_location']

        tm = TemplateMatcher(
            Template.from_registry(TemplateRegistry.STASH_BANNER))
        if tm.match(self.lf.get(Locations.STASH_BANNER)):
            # Already open.
            self.logger.log("Stash already open")
            if not gs['stash_open']:
                game_state.update({'stash_open': True})
            return

        tm = TemplateMatcher(Template.from_registry(TemplateRegistry.STASH))
        points = tm.match(self.lf.get(Locations.SCREEN_FULL))
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
            return

        self.logger.debug("Stash tab not found!. Trying center of screen.")
        self.mc.click_at_location(self.lf.get(Locations.SCREEN_CENTER))
        if tm.match(self.lf.get(Locations.STASH_BANNER)):
            # Stash open.
            game_state.update({
                'stash_open': True,
                'stash_location': self.lf.get(Locations.SCREEN_CENTER)
            })
            return

        self.logger.debug("Stash tab not found!. Placing stash tab.")
        PlaceStash().execute(game_state)

        # Stash takes time to open.
        time.sleep(2)

        if tm.match(self.lf.get(Locations.STASH_BANNER)):
            # Stash open.
            game_state.update({
                'stash_open': True,
                'stash_location': self.lf.get(Locations.SCREEN_CENTER)
            })
            return
        raise Exception("Stash not found!")


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT)

    s = OpenStash()
    gs = GameState()

    wc = WindowController()
    wc.move_to_poe()

    s.execute(gs)
