import logging

from siosa.control.game_step import Step
from siosa.control.steps.place_stash_step import PlaceStash
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations


class LocateStashStep(Step):
    def __init__(self):
        Step.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

    def execute(self, game_state):
        self.game_state = game_state
        self.logger.info("Executing step: {}".format(self.__class__.__name__))

        if game_state.get()['stash_location']:
            # Location already known.
            return

        tm = TemplateMatcher(Template.from_registry(TemplateRegistry.STASH))
        lf = LocationFactory()
        points = tm.match(lf.get(Locations.SCREEN_FULL))
        if points:
            points = points[0]
            self.logger.debug("Stash tab found@ {}".format(points))
            stash_location = lf.create(points[0], points[1], points[0], points[1])
            game_state.update({'stash_location': stash_location})
