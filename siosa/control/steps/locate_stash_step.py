import logging

from siosa.control.game_state import GameState
from siosa.control.game_step import Step, StepStatus
from siosa.control.window_controller import WindowController
from siosa.image.reusable_template_matcher import ReusableTemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


class LocateStashStep(Step):
    def __init__(self):
        Step.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def execute(self, game_state):
        """
        Args:
            game_state:
        """
        self.game_state = game_state

        if game_state.get()['stash_location']:
            # Location already known.
            return StepStatus(True)

        tm = ReusableTemplateMatcher(self.lf.get(Locations.SCREEN_FULL))
        points_s = tm.match_template(TemplateRegistry.STASH.get())
        points_gs = tm.match_template(TemplateRegistry.GUILD_STASH.get())

        if not points_s:
            # Not found.
            return StepStatus(False)

        if points_s and not points_gs:
            # Stash tab found but guild stash not found.
            point = points_s[0]
            self.logger.debug("Guild stash tab not found & Stash tab "
                              "found@ {}".format(point))
            stash_location = self.lf.create(
                point[0], point[1], point[0], point[1])
            game_state.update({'stash_location': stash_location})

        if points_s and points_gs:
            # Both are found. We need to check whether stash is from
            # "guild stash"
            gs = points_gs[0]

            points_s = [point for point in points_s if point[1] != gs[1]]
            if not points_s:
                # There are no stash points. only guild stash exists.
                return StepStatus(False)
            point = points_s[0]
            stash_location = self.lf.create(
                point[0], point[1], point[0], point[1])
            game_state.update({'stash_location': stash_location})

        return StepStatus(True)


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT)

    s = LocateStashStep()
    gs = GameState()

    wc = WindowController()
    wc.move_to_poe()

    print(s.execute(gs))
