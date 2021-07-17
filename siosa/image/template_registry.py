class TemplateRegistry:
    """Stores item_templates as enums. Values are a tuple containing the
    template file name and the resolution at which template was created.
    """
    INVENTORY_0_0 = ("sct-tmp-INVENTORY_0_0.png", (1920, 1080))
    INVENTORY = ("sct-tmp-INVENTORY.png", (1920, 1080))
    STASH = ("sct-tmp-STASH.png", (1920, 1080))
    STASH_BANNER = ("sct-tmp-STASH_BANNER.png", (1920, 1080))
    NORMAL_STASH_0_0 = ("sct-tmp-STASH_NORMAL_0_0.png", (1920, 1080))
    QUAD_STASH_0_0 = ("sct-tmp-STASH_QUAD_0_0.png", (1920, 1080))
    STASH_CLOSE_BUTTON = ("sct-tmp-STASH_CLOSE_BUTTON.png", (1920, 1080))
    DECORATIONS_BANNER = ("sct-tmp-DECORATIONS_BANNER.png", (1920, 1080))
    AWAITING_TRADE_BOX = ("sct-tmp-TRADE_AWAITING_TRADE_BOX.png", (1920, 1080))
    AWAITING_TRADE_CANCEL_BUTTON = (
        "sct-tmp-TRADE_AWAITING_TRADE_CANCEL_BUTTON.png", (1920, 1080))
    TRADE_WINDOW_TITLE = ("sct-tmp-TRADE_WINDOW_TITLE.png", (1920, 1080))
    TRADE_WINDOW_ME = ("sct-tmp-TRADE_WINDOW_ME.png", (1920, 1080))
    TRADE_WINDOW_ME_0_0 = ("sct-tmp-TRADE_WINDOW_ME_0_0.png", (1920, 1080))
    TRADE_WINDOW_ME_EMPTY_TEXT = (
        "sct-tmp-TRADE_WINDOW_ME_EMPTY_TEXT.png", (1920, 1080))
    TRADE_WINDOW_OTHER = ("sct-tmp-TRADE_WINDOW_OTHER.png", (1920, 1080))
    TRADE_WINDOW_OTHER_0_0 = (
        "sct-tmp-TRADE_WINDOW_OTHER_0_0.png", (1920, 1080))
    TRADE_WINDOW_OTHER_SMALL_0_0 = (
        "sct-tmp-TRADE_WINDOW_OTHER_SMALL_0_0.png", (1920, 1080))
    TRADE_ACCEPT_RETRACTED = (
        "sct-tmp-TRADE_ACCEPT_RETRACTED.png", (1920, 1080))
    TRADE_ACCEPT_GREEN_AURA = (
        "sct-tmp-TRADE_ACCEPT_GREEN_AURA.png", (1920, 1080))
    TRADE_ACCEPT_GREEN_AURA_ME = (
        "sct-tmp-TRADE_ACCEPT_GREEN_AURA_ME.png", (1920, 1080))
    CANCEL_TRADE_ACCEPT_BUTTON = (
        "sct-tmp-TRADE_CANCEL_ACCEPT_BUTTON.png", (1920, 1080))
    TRADE_WINDOW_OTHER_0_0_COUNT = (
        "sct-tmp-TRADE_WINDOW_OTHER_0_0_COUNT.png", (1920, 1080))
    TRADE_WINDOW_CLOSE_BUTTON = (
        "sct-tmp-TRADE_WINDOW_CLOSE_BUTTON.png", (1920, 1080))
    PARTY_NOTIFICATIONS_CLOSE_BUTTON = (
        "sct-tmp-PARTY_NOTIFICATIONS_CLOSE_BUTTON.png", (1920, 1080))
    DECORATIONS_UTILITIES_ARROW = (
        "sct-tmp-DECORATIONS_UTILITIES_ARROW.png", (1920, 1080))
    ALCHEMY_DROP = ("sct-tmp-ALCHEMY_DROP.png", (1920, 1080))
    ANCIENT_SHARD_DROP = ("sct-tmp-ANCIENT_SHARD_DROP.png", (1920, 1080))
    AWAKENED_SEXTANT_DROP = ("sct-tmp-AWAKENED_SEXTANT_DROP.png", (1920, 1080))
    CHAOS_DROP = ("sct-tmp-CHAOS_DROP.png", (1920, 1080))
    CHAOS_SHARD_DROP = ("sct-tmp-CHAOS_SHARD_DROP.png", (1920, 1080))
    EXALTED_DROP = ("sct-tmp-EXALTED_DROP.png", (1920, 1080))
    GEMCUTTER_DROP = ("sct-tmp-GEMCUTTER_DROP.png", (1920, 1080))
    HARBINGER_SHARD_DROP = ("sct-tmp-HARBINGER_SHARD_DROP.png", (1920, 1080))
    PRIME_SEXTANT_DROP = ("sct-tmp-PRIME_SEXTANT_DROP.png", (1920, 1080))
    REGAL_DROP = ("sct-tmp-REGAL_DROP.png", (1920, 1080))
    REGRET_DROP = ("sct-tmp-REGRET_DROP.png", (1920, 1080))
    SCOURING_DROP = ("sct-tmp-SCOURING_DROP.png", (1920, 1080))
    SIMPLE_SEXTANT_DROP = ("sct-tmp-SIMPLE_SEXTANT_DROP.png", (1920, 1080))
    VAAL_DROP = ("sct-tmp-VAAL_DROP.png", (1920, 1080))
    DROP = ("sct-tmp-DROP.png", (1920, 1080))
    PRICE_ITEM_WINDOW_ARROW = ("sct-tmp-PRICE_ITEM_WINDOW_ARROW.png", (1920, 1080))

    @staticmethod
    def get_template_for_currency_stack(currency_name, stack_size):
        """
        Args:
            currency_name:
            stack_size:
        """
        return "sct-tmp-{}_{}.png".format(currency_name.upper(), stack_size), (1920, 1080)
