from siosa.image.template_matcher import TemplateMatcher
from siosa.image.template_registry import TemplateRegistry
from siosa.location.location_factory import Locations


def exit_edit_hideout_mode(lf, mc):
    editing_tm = TemplateMatcher(TemplateRegistry.EDITING_BANNER.get())
    if not editing_tm.match_exists(lf.get(Locations.SCREEN_FULL)):
        return

    tm = TemplateMatcher(TemplateRegistry.DECORATIONS_EDIT_BUTTON.get())
    if not tm.match_exists(lf.get(Locations.DECORATIONS_EDIT_BOX)):
        # Decoration edit box not open.
        mc.click_at_location(lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_ARROW))

    mc.click_at_location(lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_BUTTON))
    mc.click_at_location(lf.get(Locations.DECORATIONS_EDIT_HIDEOUT_DOWN_ARROW))