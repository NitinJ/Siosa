import logging
import os

from cv2 import cv2

from siosa.common.util import parent
from siosa.image.accept_aura_template import AcceptAuraTemplate
from siosa.image.template import Template
from siosa.image.thresholding_template import ThresholdingTemplate
from siosa.image.trade_currency_template import TradeCurrencyTemplate
from siosa.image.utils import grab_screenshot
from siosa.location.location_factory import LocationFactory
from siosa.location.resolution import Resolution

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _get_template_file_path(name):
    """Returns the template output file path given name of the template.
    :param name: Template name

    Args:
        name:

    Returns:
        Full file path of the template file.
    """
    siosa_base = parent(parent(__file__))
    return os.path.join(
        siosa_base, "resources/templates/{}".format(name))


class TemplateWrapper:
    def __init__(self, name, resolution, template_class=Template):
        self.name = name
        self.resolution = resolution
        self.template_class = template_class
        self.template = None

    def get(self):
        if self.template:
            return self.template
        file_path = _get_template_file_path(self.name)
        logger.debug("Template file path: {}".format(file_path))
        self.template = self.template_class(
            self.name,
            file_path,
            Resolution(*self.resolution))
        return self.template


class TemplateRegistry:
    """Stores item_templates as enums. Values are a tuple containing the
    template file name and the resolution at which template was created.
    """
    INVENTORY_0_0 = TemplateWrapper("sct-tmp-INVENTORY_0_0.png", (1920, 1080))
    STASH = TemplateWrapper("sct-tmp-STASH.png", (1920, 1080),
                            template_class=ThresholdingTemplate)
    GUILD_STASH = TemplateWrapper("sct-tmp-GUILD_STASH.png", (1920, 1080),
                                  template_class=ThresholdingTemplate)
    TANE = TemplateWrapper("sct-tmp-TANE.png", (1920, 1080),
                            template_class=ThresholdingTemplate)
    STASH_BANNER = TemplateWrapper("sct-tmp-STASH_BANNER.png", (1920, 1080))
    NORMAL_STASH_0_0 = TemplateWrapper("sct-tmp-STASH_NORMAL_0_0.png",
                                       (1920, 1080))
    QUAD_STASH_0_0 = TemplateWrapper("sct-tmp-STASH_QUAD_0_0.png", (1920, 1080))
    AWAITING_TRADE_CANCEL_BUTTON = TemplateWrapper(
        "sct-tmp-TRADE_AWAITING_TRADE_CANCEL_BUTTON.png", (1920, 1080))
    TRADE_WINDOW_ME_EMPTY_TEXT = TemplateWrapper(
        "sct-tmp-TRADE_WINDOW_ME_EMPTY_TEXT.png", (1920, 1080),
        template_class=ThresholdingTemplate)
    TRADE_WINDOW_OTHER_SMALL_0_0 = TemplateWrapper(
        "sct-tmp-TRADE_WINDOW_OTHER_SMALL_0_0.png", (1920, 1080))
    TRADE_ACCEPT_RETRACTED = TemplateWrapper(
        "sct-tmp-TRADE_ACCEPT_RETRACTED.png", (1920, 1080))
    TRADE_ACCEPT_GREEN_AURA = TemplateWrapper(
        "sct-tmp-TRADE_ACCEPT_GREEN_AURA.png", (1920, 1080),
        template_class=AcceptAuraTemplate)
    CANCEL_TRADE_ACCEPT_BUTTON = TemplateWrapper(
        "sct-tmp-TRADE_CANCEL_ACCEPT_BUTTON.png", (1920, 1080))
    TRADE_WINDOW_CLOSE_BUTTON = TemplateWrapper(
        "sct-tmp-TRADE_WINDOW_CLOSE_BUTTON.png", (1920, 1080))
    PARTY_NOTIFICATIONS_CLOSE_BUTTON = TemplateWrapper(
        "sct-tmp-PARTY_NOTIFICATIONS_CLOSE_BUTTON.png", (1920, 1080))
    DECORATIONS_UTILITIES_ARROW = TemplateWrapper(
        "sct-tmp-DECORATIONS_UTILITIES_ARROW.png", (1920, 1080))
    DECORATIONS_EDIT_BUTTON =  TemplateWrapper(
        "sct-tmp-DECORATIONS_EDIT_BUTTON.png", (1920, 1080))
    EDITING_BANNER =  TemplateWrapper(
        "sct-tmp-EDITING_BANNER.png", (1920, 1080))
    INVENTORY_BANNER = TemplateWrapper("sct-tmp-INVENTORY_BANNER.png",
                                       (1920, 1080))
    DROP = TemplateWrapper("sct-tmp-DROP.png", (1920, 1080))
    PRICE_ITEM_WINDOW_ARROW = TemplateWrapper(
        "sct-tmp-PRICE_ITEM_WINDOW_ARROW.png", (1920, 1080))

    @staticmethod
    def get_template_for_currency_stack(currency_name, stack_size):
        """
        Args:
            currency_name:
            stack_size:
        """
        return TemplateWrapper("sct-tmp-{}_{}.png".format(
            currency_name.upper(), stack_size), (1920, 1080),
            template_class=TradeCurrencyTemplate)

    @staticmethod
    def create(name, location, overwrite=False, debug=False):
        """Creates a template with a given name by capturing screen at the given
        location. :param name: Name of the file, in which template image will be
        stored. :param location: Screen location to capture and create template
        from. :param overwrite: Whether to overwrite the template file if it
        already

            exists.

        Args:
            name:
            location:
            overwrite:
            debug:

        Returns:
            The full template file path
        """
        output_file_path = _get_template_file_path(
            "sct-tmp-{}.png".format(name))

        if os.path.isfile(output_file_path):
            logger.info(
                'Template already exists at {}'.format(output_file_path))
            if not overwrite:
                return output_file_path

        image_bytes_rgb = grab_screenshot(location)
        if debug:
            cv2.imshow('Template', image_bytes_rgb)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        cv2.imwrite(output_file_path, image_bytes_rgb)
        logger.debug('Created template at: {}'.format(output_file_path))
        return Template(name, output_file_path, LocationFactory().resolution)

    @staticmethod
    def create_from_file(name, input_file_path, overwrite=False, debug=False):
        """Creates a template with a given name from the image present at the
        given file system location. :param name: Name of the file, in which
        template image will be stored. :param input_file_path: File system path
        of the image to create template :param from.: :param overwrite: Whether
        to overwrite the template file if it already

            exists.

        Args:
            name:
            input_file_path:
            overwrite:
            debug:

        Returns:
            The full template file path
        """
        if not os.path.isfile(input_file_path):
            logger.info(
                'No input file exists at {}'.format(input_file_path))
            return None

        output_file_path = _get_template_file_path(
            "sct-tmp-{}.png".format(name))

        if os.path.isfile(output_file_path):
            logger.info(
                'Template already exists at {}'.format(output_file_path))
            if not overwrite:
                return output_file_path

        image = cv2.imread(input_file_path)
        cv2.imwrite(output_file_path, image)

        if debug:
            cv2.imshow('Template', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        logger.debug('Created template at: {}'.format(output_file_path))
        return Template(name, output_file_path, LocationFactory().resolution)
