import pywinauto as pwa

class WindowController:
    def __init__(self):
        pass

    def move_to_poe(self):
        app = pwa.application.Application()
        app.connect(title_re='Path of Exile')
        app_dialog = app.window()
        app_dialog.set_focus()
