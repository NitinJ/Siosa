FIELDS = [
    {
        "name": "account_name",
        "desc": "Account name",
        "required": True,
        "default": ""
    },
    {
        "name": "poe_session_id",
        "desc": "Poe session id (POESESSID)",
        "required": True,
        "default": ""
    },
    {
        "name": "client_log_file_path",
        "desc": "Path to PathOfExile's client.txt log file",
        "required": True,
        "default": ""
    },
    {
        "name": "league",
        "desc": "League",
        "required": True,
        "default": "Standard",
    },
    {
        "name": "license_key",
        "desc": "License key",
        "required": True,
        "default": ""
    },
    {
        "name": "dump",
        "desc": "Name of the stash tabs to put items into",
        "required": True,
        "default": [],
    },
    {
        "name": "currency",
        "desc": "Name of the currency tabs to put currency in",
        "required": True,
        "default": [],
    },
    {
        "name": "sell",
        "desc": "Name of the stash tabs to sell items from",
        "required": True,
        "default": [],
    },
    {
        "name": "close_all_user_interface",
        "desc": "PathOfExile's shortcut keys to close all interfaces",
        "required": False,
        "default": ["Ctrl", "`"]
    },
    {
        "name": "task_stop",
        "desc": "Shortcut keys to stop all running siosa tasks",
        "required": False,
        "default": "Ctrl+q"
    }
]


def get_required_fields():
    return [field for field in FIELDS if field['required']]


def get_optional_fields():
    return [field for field in FIELDS if not field['required']]


def get_metadata():
    return FIELDS


def get_field_names():
    return [field['name'] for field in FIELDS]


def get_default_config():
    default_config = {}
    for field in FIELDS:
        default_config[field['name']] = field['default']
    return default_config
