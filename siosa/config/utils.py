import logging
import os

from license.license import License
from siosa.config.metadata import get_required_fields
from siosa.network.poe_api import PoeApi

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def validate_config(config):
    if not config:
        return False, ''
    for field in get_required_fields():
        logger.debug("Validating field: {}".format(field['name']))
        if field['name'] not in config.keys():
            logger.debug(
                "Required field {} not in config".format(field['name']))
            return False, field['name']
        validator = get_validator_for_field(field['name'])
        if not validator or not validator(config[field['name']], config):
            logger.debug(
                "Validation failed for field: {}".format(field['name']))
            return False, field['name']
        logger.debug("Validation success for field: {}".format(field['name']))
    return True, ''


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
    for stash in get_stash_metadata(config_json):
        if stash['n'].lower() in names:
            return True
    return False


def validate_stash_tab_indexes(indexes, config_json):
    for stash in get_stash_metadata(config_json):
        if stash['i'] in indexes:
            return True
    return False


def get_stash_metadata(config_json):
    account_name = config_json.get('account_name', None)
    session_id = config_json.get('poe_session_id', None)
    league = config_json.get('league', None)
    if not account_name or not session_id or not league:
        return []
    poe_api = PoeApi(account_name, session_id, league=league)
    return poe_api.get_stash_metadata(refresh=False).get('tabs', [])
