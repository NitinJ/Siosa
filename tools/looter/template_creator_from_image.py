import pyautogui

from siosa.image.template import Template
from siosa.location.location_factory import LocationFactory, Locations

lf = LocationFactory()


def create_template(name, template_path):
    """
    Args:
        name:
        template_path:
    """
    Template.create_from_file(name, template_path, overwrite=True, debug=True)


if __name__ == "__main__":
    templates = [
        # ['ALCHEMY_DROP', 'alchemy.jpg'],
        # ['ANCIENT_SHARD_DROP', 'ancient_shard.jpg'],
        # ['AWAKENED_SEXTANT_DROP', 'awakened_sextant.jpg'],
        ['DROP', 'drop.jpg'],
        # ['CHAOS_SHARD_DROP', 'chaos_shard.jpg'],
        # ['EXALTED_DROP', 'exalted.jpg'],
        # ['GEMCUTTER_DROP', 'gemcutter.jpg'],
        # ['HARBINGER_SHARD_DROP', 'harbinger_shard.jpg'],
        # ['PRIME_SEXTANT_DROP', 'prime_sextant.jpg'],
        # ['REGAL_DROP', 'regal.jpg'],
        # ['REGRET_DROP', 'regret.jpg'],
        # ['SCOURING_DROP', 'scouring.jpg'],
        # ['SIMPLE_SEXTANT_DROP', 'simple_sextant.jpg'],
        # ['VAAL_DROP', 'vaal.jpg']
    ]
    for template in templates:
        create_template(template[0], template[1])
