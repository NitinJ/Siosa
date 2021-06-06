def item_contains_all_affixes(in_game_item, affixes):
    return all([item_contains_affix(
        in_game_item, affix) for affix in affixes])


def item_contains_affix(in_game_item, affix):
    if affix.type == 'prefix':
        return affix_match_any(in_game_item.get_prefixes(), affix)
    return affix_match_any(in_game_item.get_suffixes(), affix)


def affix_match_any(affixes, required_affix):
    return any([affix_match(affix, required_affix) for affix in affixes])


def affix_match_all(affixes, required_affix):
    return all([affix_match(affix, required_affix) for affix in affixes])


def affix_match(affix, required_affix):
    if affix.type != required_affix.type:
        return False
    if required_affix.name and affix.name != required_affix.name:
        return False
    if required_affix.tier and affix.tier > required_affix.tier:
        return False
    if required_affix.str_val:
        return affix.str_val.find(required_affix.str_val) > -1
    return True
