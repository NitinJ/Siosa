from siosa.config.siosa_config import SiosaConfig
from siosa.control.game_step import Step, StepStatus


class CloseAllWindows(Step):
    def execute(self, game_state):
        self.kc.keypress_with_modifiers(
            SiosaConfig().get_close_all_interfaces_shortcut())
        game_state.update({'stash_open': False, 'inventory_open': False})
        return StepStatus(True)
