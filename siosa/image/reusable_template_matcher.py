from siosa.image.template_matcher import TemplateMatcher


class ReusableTemplateMatcher(TemplateMatcher):
    def __init__(self, location, confidence=0.75, debug=False,
                 confirm_foreground=False, scale=1.0):
        """
        Args:
            location:
            confidence:
            debug:
            confirm_foreground:
            scale:
        """
        TemplateMatcher.__init__(self,
                                 None,
                                 confidence=confidence,
                                 debug=debug,
                                 confirm_foreground=confirm_foreground,
                                 scale=scale)
        self.location = location

    def match_template(self, template):
        """
        Args:
            template:
        """
        self.template = template
        return self.match(self.location, reuse=True)
