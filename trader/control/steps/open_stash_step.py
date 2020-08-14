from control.game_step import Step

class OpenStash(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
    
    def execute(self):
        self.logger.info("Executing step: OpenStash")
        if not self.game_state.get()['stash_open']:
            game_state = self.game_state.get()
            self.mc.click_at_location(game_state['stash_location'])
            self.game_state.update({'stash_open': True})
