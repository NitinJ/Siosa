from siosa.control.console_controller import ConsoleController
from siosa.control.keyboard_controller import KeyboardController
from siosa.control.window_controller import WindowController

COMMANDS = {
    'INVITE_CHARACTER': "/invite {}"
}

def invite_character_to_party(character_name):
    window_controller = WindowController()
    window_controller.move_to_poe()
    cc = ConsoleController()
    cc.send_chat(character_name, "Please join my party !")
    cc.console_command(COMMANDS['INVITE_CHARACTER'].format(character_name))