from siosa.image.template_matcher import TemplateMatcher
from siosa.location.in_game_location import InGameLocation


class ReusableTemplateMatcher(TemplateMatcher):
    def __init__(self, location: InGameLocation, confidence=0.75, debug=False, scale=1.0):
        """
        Args:
            location:
            confidence:
            debug:
            scale:
        """
        TemplateMatcher.__init__(self,
                                 None,
                                 confidence=confidence,
                                 debug=debug,
                                 scale=scale)
        self.location = location

    def match_template(self, template):
        """
        Args:
            template:
        """
        self.template = template
        return self.match(self.location, reuse=True)
