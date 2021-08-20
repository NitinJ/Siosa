import logging
import os

from license.license import License
from siosa.config.metadata import get_required_fields, get_field_names
from siosa.network.poe_api import PoeApi

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate_fields(config_json, full_config_json):
    """
    validates whether given field_name: field_value are correct. Doesn't check
    whether all required fields are present or not.
    Args:
        config_json:

    Returns: An valid_status json with field_name: status, status='valid' if
    field_value is correct else 'invalid'

    """
    if not config_json:
        return {}

    valid_status = config_json.copy()
    all_field_names = get_field_names()
    for field_name, field_value in config_json.items():
        if field_name not in all_field_names:
            valid_status[field_name] = 'invalid'
            logger.debug("{} : {}".format(field_name, 'invalid'))
            continue

        validator = get_validator_for_field(field_name)
        if not validator or not validator(field_value, full_config_json):
            valid_status[field_name] = 'invalid'
            logger.debug("{} : {}".format(field_name, 'invalid'))
            continue

        logger.debug("{} : {}".format(field_name, 'valid'))
        valid_status[field_name] = 'valid'
    return valid_status


def get_validator_for_field(field_name: str):
    if field_name == "account_name":
        return validate_account_name
    elif field_name == "poe_session_id":
        return validate_poe_session_id
    elif field_name == "league":
        return validate_league
    elif field_name == "client_log_file_path":
        return validate_client_file_path
    elif field_name == "license_key":
        return validate_license_key
    elif field_name in ("dump", "currency", "sell"):
        return validate_stash_tab_names
    elif field_name in ("close_all_user_interface", "task_stop"):
        # TODO: Add an actual validator.
        return lambda value, json: True
    else:
        return None


def validate_account_name(account_name, config_json):
    if not account_name:
        return False
    characters = PoeApi.get_characters(account_name)
    return not not characters


def validate_poe_session_id(session_id, config_json):
    if not session_id:
        return False
    profile = PoeApi.get_profile(session_id)
    return 'error' not in profile.keys()


def validate_league(league, config_json):
    if not league:
        return False
    league_names = [league['id'].lower() for league in PoeApi.get_leagues()]
    return league.lower() in league_names


def validate_client_file_path(client_file_path, config_json):
    return os.path.isfile(client_file_path)


def validate_license_key(license_key, config_json):
    return License.valid(license_key)


def validate_stash_tab_names(names, config_json):
    stashes = [stash['n'].lower() for stash in get_stash_metadata(config_json)]
    for name in names:
        if name.lower() not in stashes:
            return False
    return True


def validate_stash_tab_indexes(indexes, config_json):
    stash_indexes = \
        [int(stash['i']) for stash in get_stash_metadata(config_json)]
    for index in indexes:
        if int(index) not in stash_indexes:
            return False
    return True


def get_stash_metadata(config_json):
    account_name = config_json.get('account_name', None)
    session_id = config_json.get('poe_session_id', None)
    league = config_json.get('league', None)
    if not account_name or not session_id or not league:
        return []
    poe_api = PoeApi(account_name, session_id, league)
    return poe_api.get_stash_metadata(refresh=False).get('tabs', [])
