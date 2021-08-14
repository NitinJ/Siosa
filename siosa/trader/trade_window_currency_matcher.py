import numpy as np

from siosa.image.reusable_template_matcher import ReusableTemplateMatcher
from siosa.location.in_game_location import InGameLocation


class TradeWindowCurrencyMatcher(ReusableTemplateMatcher):
    """Matcher for specifically matching currencies in the trade window_other.
    Removes the green channel from the image before matching. Template used
    should also not have the green channel.
    """
    def __init__(self, location: InGameLocation, debug=False, scale=1.0):
        """
        Args:
            location:
            debug:
            scale:
        """
        ReusableTemplateMatcher.__init__(self, location, confidence=0.88,
                                         debug=debug,
                                         scale=scale)

    def get_image(self, screen_location, reuse):
        """
        Args:
            screen_location:
            reuse:
        """
        image_bytes_bgr, image_bytes_gray = super().get_image(screen_location,
                                                              reuse)
        # Remove the green channel from the screen area to remove the green
        # hazy border when trade has been accepted by the other player.
        image_bytes_bgr[:, :, 1] = np.zeros(
            [image_bytes_bgr.shape[0], image_bytes_bgr.shape[1]])
        return image_bytes_bgr, image_bytes_gray
