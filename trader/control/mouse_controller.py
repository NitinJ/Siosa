from ..common.decorations import singleton
import pyautogui

@singleton
class MouseController:
	def __init__(self, location_factory, mouse_move_duration=0.015, mouse_movement_curve=pyautogui.easeInOutQuad):
	 	self.location_factory = location_factory
		self.current_location = self.location_factory.create(0, 0, 0, 0)
		self.mouse_move_duration = mouse_move_duration
		self.mouse_movement_curve = mouse_movement_curve

	def move_mouse(self, location):
		if location.equals(self.current_location):
			return
		point = location.get_random_point()
		pyautogui.moveTo(point[0], point[1], self.mouse_move_duration, self.mouse_movement_curve)
		self.current_location = location

	def right_click(self):
		pyautogui.click(button='right')

	def click(self):
		pyautogui.click(button='left')

	def get_current_location(self):
		return self.current_location
