from siosa.control.game_step import Step


class CloseAllWindows(Step):
    def execute(self, game_state):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.kc.hold_modifier('Ctrl')
        self.kc.keypress("`")
        self.kc.unhold_modifier('Ctrl')
        game_state.update({'stash_open': False, 'inventory_open': False})
