from siosa.common.decorations import override
from siosa.image.template_matcher import TemplateMatcher
from siosa.location.in_game_location import InGameLocation


class ReusableTemplateMatcher(TemplateMatcher):
    def __init__(self, location: InGameLocation, threshold=0.80, debug=False,
                 scale=1.0):
        TemplateMatcher.__init__(self,
                                 None,
                                 threshold=threshold,
                                 debug=debug,
                                 scale=scale)
        self.location = location

    @override
    def match_template(self, template):
        """
        Args:
            template:
        """
        self.template = template
        return self.match(self.location, reuse=True)

    @override
    def match_exists(self, template):
        self.template = template
        return super().match_exists(self.location, reuse=True)
