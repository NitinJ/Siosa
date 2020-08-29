from siosa.control.game_step import Step


class OpenStash(Step):
    def execute(self, game_state):
        self.logger.info("Executing step: OpenStash")
        state = game_state.get()
        if not state['stash_open']:
            self.mc.click_at_location(state['stash_location'])
            game_state.update({'stash_open': True})
