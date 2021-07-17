import cProfile
import logging
import pstats
import time

from pynput import keyboard

from siosa.control.keyboard_controller import KeyboardController
from siosa.control.mouse_controller import MouseController
from siosa.image.reusable_template_matcher import ReusableTemplateMatcher
from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import LocationFactory, Locations

lf = LocationFactory()

FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)



class KeyboardShortcut:
    def __init__(self, combination, callback):
        """
        Args:
            combination:
            callback:
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.combination = combination
        self.current_key_set = set()
        self.callback = callback
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(self.combination),
            self.on_activate)
        self.listener = keyboard.Listener(
            on_press=self.for_canonical(hotkey.press),
            on_release=self.for_canonical(hotkey.release))

    def for_canonical(self, f):
        """
        Args:
            f:
        """
        return lambda k: f(self.listener.canonical(k))

    def start_listening(self):
        self.listener.start()
        self.logger.info("Started listening to keyboard shortcut.")

    def on_activate(self):
        self.callback()


def _create_matchers(item_templates):
    """
    Args:
        item_templates:
    """
    matchers = {}
    for template in item_templates:
        matchers[template] = TemplateMatcher(template, debug=debug,
                                             scale=Looter.SCALE_FACTOR)
    return matchers


def _create_template(template_from_registry):
    """
    Args:
        template_from_registry:
    """
    return Template.from_registry(template_from_registry,
                                  scale=Looter.SCALE_FACTOR)

debug = True
class Looter:
    COMBINATIONS = '<ctrl>+<alt>+l'
    MOVEMENT_CHECK_DURATION = 0.01
    # Based on maximum 5 seconds to reach location.
    MOVEMENT_CHECK_MAX_TRIES = 100
    SCALE_FACTOR = 0.75

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.keyboard_listener = KeyboardShortcut(Looter.COMBINATIONS,
                                                  self.flip_looting)
        self.should_loot = False
        self.item_templates = [
            # _create_template(TemplateRegistry.ALCHEMY_DROP),
            # _create_template(TemplateRegistry.ANCIENT_SHARD_DROP),
            # _create_template(TemplateRegistry.AWAKENED_SEXTANT_DROP),
            # _create_template(TemplateRegistry.CHAOS_DROP),
            # _create_template(TemplateRegistry.CHAOS_SHARD_DROP),
            # _create_template(TemplateRegistry.EXALTED_DROP),
            # _create_template(TemplateRegistry.GEMCUTTER_DROP),
            # _create_template(TemplateRegistry.HARBINGER_SHARD_DROP),
            # _create_template(TemplateRegistry.PRIME_SEXTANT_DROP),
            # _create_template(TemplateRegistry.REGAL_DROP),
            # _create_template(TemplateRegistry.REGRET_DROP),
            # _create_template(TemplateRegistry.SCOURING_DROP),
            # _create_template(TemplateRegistry.SIMPLE_SEXTANT_DROP),
            # _create_template(TemplateRegistry.VAAL_DROP),
            _create_template(TemplateRegistry.DROP)
        ]
        self.matchers = _create_matchers(self.item_templates)
        self.lf = LocationFactory()
        self.mc = MouseController(self.lf)
        self.kc = KeyboardController()

    def flip_looting(self):
        self.should_loot = (not self.should_loot)

    def start_looting(self):
        self.keyboard_listener.start_listening()
        self._loot()

    def _dedupe_locations(self, locations):
        """
        Args:
            locations:
        """
        if not locations or len(locations) == 1:
            return locations
        before = locations[0]
        deduped_locations = [before]
        for i in range(1, len(locations)):
            now = locations[i]
            if now[1] - before[1] != 1:
                deduped_locations.append(now)
            before = now
        return deduped_locations

    def _find_all_items(self):
        item_locations_with_template = []
        full_screen_matcher = \
            ReusableTemplateMatcher(Locations.SCREEN_FULL, debug=debug,
                                    scale=Looter.SCALE_FACTOR)
        for template in self.item_templates:
            locations = full_screen_matcher.match_template(template)
            locations = self._dedupe_locations(locations)
            for location in locations:
                item_locations_with_template.append({
                    'template': template,
                    'location': location
                })
        return item_locations_with_template

    def find_nearest_location_from_screen_center(self, template_locations):
        """
        Args:
            template_locations:
        """
        center = self.lf.get(Locations.SCREEN_CENTER).get_scaled_location(
            Looter.SCALE_FACTOR).get_center()

        def distance_from_center(template_location):
            location = template_location['location']
            xd = (location[0] - center[0])
            yd = (location[1] - center[1])
            return xd * xd + yd * yd

        template_locations.sort(key=distance_from_center)
        return template_locations[0]

    def get_bounding_location_for_template(self, template):
        """
        Args:
            template:
        """
        width, height = template.get_dimensions()
        center = self.lf.get(Locations.SCREEN_CENTER).get_scaled_location(
            Looter.SCALE_FACTOR).get_center()
        x1 = center[0] - 2*width
        x2 = center[0] + 2*width
        y1 = center[1] - int((2.5) * height)
        y2 = center[1] - height / 2
        return self.lf.create(x1, y1, x2, y2).get_scaled_location(
            1 / Looter.SCALE_FACTOR)

    def _loot(self):
        while True:
            if not self.should_loot:
                time.sleep(0.01)
                continue

            # Find all item locations with the associated template.
            item_locations_with_template = self._find_all_items()
            if not item_locations_with_template:
                # No items found.
                self.should_loot = False
                continue

            # Nearest item location with it's template
            item_location_with_template = self.find_nearest_location_from_screen_center(
                item_locations_with_template)

            template = item_location_with_template['template']
            raw_location = item_location_with_template['location']
            location = self.lf.create(
                raw_location[0],
                raw_location[1],
                raw_location[0],
                raw_location[1]).get_scaled_location(1 / Looter.SCALE_FACTOR)

            # In game, resolution scaled bounding box for template. width: 2W,
            # height: 2H, from center.
            bbox = self.get_bounding_location_for_template(template)

            # Right click on location.
            self.mc.click_at_location(location, 'right')

            # Check in loop if template matches center +- template width.
            ntries = 0
            reached = True
            while not self.matchers[template].match(bbox):
                ntries += 1
                if ntries >= Looter.MOVEMENT_CHECK_MAX_TRIES:
                    reached = False
                    self.logger.error("Exceeded tries to reach item")
                    break
                time.sleep(Looter.MOVEMENT_CHECK_DURATION)

            if not reached:
                # We didn't find the item. Something went wrong.
                self.should_loot = False
                continue

            # Pickup item.
            self.mc.click_at_location(bbox.get_center_location(), 'left')

            # Hide, unhide items.
            self.kc.keypress('.')
            self.kc.keypress('.')
            time.sleep(0.01)


if __name__ == "__main__":
    l = Looter()
    l.start_looting()
