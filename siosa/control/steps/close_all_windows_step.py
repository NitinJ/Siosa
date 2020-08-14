from control.game_step import Step

class CloseAllWindows(Step):
    def __init__(self, game_state):
        Step.__init__(self, game_state)
    
    def execute(self):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.kc.hold_modifier('Ctrl')
        self.kc.keypress("`")
        self.kc.unhold_modifier('Ctrl')
        self.game_state.update({'stash_open': False, 'inventory_open': False})

