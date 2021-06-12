from siosa.image.template import Template
from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry


class ReusableTemplateMatcher(TemplateMatcher):
    def __init__(self, location, confidence=0.75, debug=False,
                 confirm_foreground=False, scale=1.0):
        TemplateMatcher.__init__(self,
                                 Template.from_registry(TemplateRegistry.STASH),
                                 confidence=confidence, debug=debug,
                                 confirm_foreground=confirm_foreground)
        self.location = location

    def match_template(self, template):
        self.template = template
        return self.match(self.location, reuse=True)
