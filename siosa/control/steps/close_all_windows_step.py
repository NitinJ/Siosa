from siosa.control.game_step import Step
from siosa.config.siosa_config import SiosaConfig

class CloseAllWindows(Step):
    def execute(self, game_state):
        self.logger.info("Executing step: {}".format(self.__class__.__name__))
        self.kc.keypress_with_modifiers(
            SiosaConfig().config['shortcuts']['close_all_user_interface'])
        game_state.update({'stash_open': False, 'inventory_open': False})
