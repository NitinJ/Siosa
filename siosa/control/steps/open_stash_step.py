from siosa.control.game_step import Step
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations, LocationFactory


class OpenStash(Step):
    def execute(self, game_state):
        self.logger.info("Executing step: OpenStash")
        tm = TemplateMatcher(Template.from_registry(TemplateRegistry.STASH_BANNER))

        lf = LocationFactory()
        points = tm.match(lf.get(Locations.STASH_BANNER))

        if points:
            # Already open
            game_state.update({'stash_open': True})
            return

        state = game_state.get()
        if not state['stash_open'] and state['stash_location']:
            self.mc.click_at_location(state['stash_location'])
            game_state.update({'stash_open': True})
