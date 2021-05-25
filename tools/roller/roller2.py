################################################################################
# @Author: MopedDriver
# Item roller for alteration crafting.
################################################################################

import json
import random
import time
import tkinter as tk
from pprint import pformat
from time import sleep
from time import strftime

import pyautogui
import win32clipboard
from overlay import Window
from scanf import scanf

################################################################################
# Config
AFFIX_FILE = "config.json"

LOG_FILE = "log.txt"
MOUSE_MOVE_DELAY = 0.01
MOUSE_MOVE_DURATION = 0.01
ROLL_DELAY = 0.01
KEY_PRESS_DELAY = 0.01
MAX_ROLLS = 1500
CLIPBOARD_READ_SLEEP_TIME = 0.15

# Won't use currency if debug mode is set.
DEBUG_MODE = True

################################################################################
# Globals as per 1920x1080px
CURRENCY_LOCATION = {
    'orb of alteration': (114, 263, 114, 263),
    'orb of augmentation': (233, 318, 233, 318),
    'regal orb': (431, 263, 431, 263),
    'orb of scouring': (176, 445, 176, 445),
    'orb of transmutation': (56, 268, 56, 268)
}
ITEM_LOCATION = (336, 419, 336, 419)
INVENTORY_00 = (1295, 615, 1295, 615)
INVENTORY_SLOT_SIZE = 53
SUPPORTED_RARITIES = ['magic', 'rare']
LINE_FEED = "\r\n"

################################################################################
# State
# Once
required_state = {}
down_keys = {}
# Per item.
item_state = {
    "rarity": "normal",
    "mods": {
        "prefix": None,
        "suffix": None
    }
}
currency_state = {'picked_up_currency': None}
location_state = ITEM_LOCATION


################################################################################
def set_clipboard_data(data):
    try:
        win32clipboard.OpenClipboard()
    except:
        time.sleep(CLIPBOARD_READ_SLEEP_TIME)
        win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(data)
    win32clipboard.CloseClipboard()


def get_clipboard_data():
    # get clipboard data
    try:
        win32clipboard.OpenClipboard()
    except:
        time.sleep(CLIPBOARD_READ_SLEEP_TIME)
        win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    set_clipboard_data('')
    return data.lower()


def parse_currency_from_clipboard():
    data = get_clipboard_data()
    if data == '':
        return {'count': 0}
    split_data = data.split("--------\r\n")
    type = split_data[0].split(LINE_FEED)[2]
    count = int(split_data[1].split("stack size: ")
                [1].split("/")[0].replace(',', ''))
    currency_state[type] = count


def read_item_rolls():
    copy_item_at_cursor()
    read_affixes(get_clipboard_data())
    log(json.dumps(item_state))


def get_prefix_suffix_names(data):
    name = get_name(data)
    rarity = get_rarity(data)
    print("[Debug] Full item name: ", name)

    if rarity == 'rare':
        return {'prefix': '', 'suffix': ''}

    base = required_state['base_name']
    suffix = None
    prefix = None
    if name.find(base) > 0:
        prefix = name[0:name.find(base)].strip().lower()
    if name.find(" of ") != -1:
        suffix = name[name.find(" of ") + 1:].strip().lower()
    return {'prefix': prefix, 'suffix': suffix}


def get_rarity(data):
    name_section_lines = data.split("--------\r\n")[0].split(LINE_FEED)
    rarity_str = "rarity: "
    rarity = None
    for line in name_section_lines:
        r = line.find(rarity_str)
        if r == -1:
            continue
        rarity = line[r + len(rarity_str):].strip().lower()
        break
    print("[Debug] Item rarity: ", rarity)
    return rarity


def get_name(data):
    rarity = get_rarity(data)
    name = ''
    name_section = data.split("--------\r\n")[0]
    if rarity == 'magic':
        name = name_section.split(LINE_FEED)[2].strip().lower()
    elif rarity == 'rare':
        name = " ".join(name_section.split(LINE_FEED)[2:]).lower()
    print("[Debug] Item name: ", name)
    return name


def get_mod_section_for_cluster_jewel(data):
    return data.split("--------\r\n")[-2]


def get_mod_section(data):
    name = get_name(data)
    rarity = get_rarity(data)
    if rarity == 'normal':
        return ''
    if name.find("cluster jewel") > -1:
        return get_mod_section_for_cluster_jewel(data)
    elif name.find("watchstone") > -1:
        mods_section = data.split("--------\r\n")[2]
        if mods_section.find("enchant") > -1:
            mods_section = data.split("--------\r\n")[3]
        return mods_section
    else:
        mods_section = data.split("--------\r\n")[4]
        if mods_section.find("item level") != -1:
            mods_section = data.split("--------\r\n")[5]
        if mods_section.find("implicit") != -1:
            mods_section = data.split("--------\r\n")[6]
        return mods_section


def get_all_mods(data):
    mods_section = get_mod_section(data)
    mods = []
    for mod in mods_section.split(LINE_FEED):
        if mod.strip().lower():
            mods.append(mod.strip().lower())

    print("[Debug] All item mods: ", mods)
    return mods


def read_affixes(data):
    print("[Debug] data before reading affixes", data)
    ret = get_prefix_suffix_names(data)
    ret['all_mods'] = get_all_mods(data)
    item_state['mods'] = ret
    item_state['rarity'] = get_rarity(data)


def log(s):
    if flog:
        flog.write(strftime("%a, %d %b %I:%M:%S %p : ") + s + "\n")


def single_affix_match(affix, required_tier):
    affix_tier = affix.split("tier: ")[1].split(")")[0]
    if affix_tier <= required_tier:
        log("found")
        return True
    else:
        log("tier didn't match")
        return False


def exact_affix_matches(current_affixes, required_affix_tier):
    if not required_affix_tier:
        # Required mod option affixes are empty so no need to match.
        return True
    if current_affixes:
        for affix in current_affixes:
            if single_affix_match(affix, required_affix_tier):
                return True
    return False


def prefix_match(current, required_mod_option):
    if required_mod_option['prefix'] and current['mods']['prefix']:
        # Prefix present
        if required_mod_option['prefix'] != current['mods']['prefix']:
            return False
        elif not exact_affix_matches(current['mods']['all_mods'],
                                     required_mod_option['prefix_tier']):
            # Prefix is equal to the required one but exact prefix isn't in
            # exact required list.
            print("Exact prefix didn't match !")
            return False
        return True
    return False


def suffix_match(current, required_mod_option):
    if required_mod_option['suffix'] and current['mods']['suffix']:
        # suffix present
        if required_mod_option['suffix'] != current['mods']['suffix']:
            return False
        elif not exact_affix_matches(current['mods']['all_mods'],
                                     required_mod_option['suffix_tier']):
            # suffix is equal to the required one but exact suffix isn't in exact required list.
            print("Exact suffix didn't match !")
            return False
        return True
    return False


def magic_mod_check(current, required):
    print("Magic mod check: current_key_set : {}".format(
        pformat(current['mods'])))

    for mod_option in required['magic_mods']:
        print("Checking required mod_option: ", mod_option)

        if mod_option['prefix']:
            # Prefix present
            if mod_option['prefix'] != current['mods']['prefix']:
                # Prefix is not equal to the required one.
                print("Prefix didn't match !")
                continue
            elif not exact_affix_matches(current['mods']['all_mods'],
                                         mod_option['prefix_tier']):
                # Prefix is equal to the required one but exact prefix isn't in
                # exact required list.
                print("Exact affix didn't match !")
                continue
        if mod_option['suffix']:
            if mod_option['suffix'] != current['mods']['suffix']:
                print("Suffix didn't match !")
                continue
            elif not exact_affix_matches(current['mods']['all_mods'],
                                         mod_option['suffix_tier']):
                print("Suffix didn't match !")
                continue
        log("[Debug] Mod match" + json.dumps(mod_option))
        return True
    return False


def rare_mod_check(current, required):
    print("Checking rare mods")
    for required_rare_mod in required['rare_mods']:
        if required_rare_mod not in current['mods']['all_mods']:
            print(
                "[Debug] Rare mod didn't match : {}".format(required_rare_mod))
            log("[Debug] Rare mod didn't match : {}".format(required_rare_mod))
            return False
    return True


def move_mouse(location):
    global location_state
    if location_state == location:
        # Already in the same location
        return
    sleep(MOUSE_MOVE_DELAY)
    x1, y1, x2, y2 = location
    x = random.randint(x1, x2)
    y = random.randint(y1, y2)
    pyautogui.moveTo(x, y, MOUSE_MOVE_DURATION, pyautogui.easeInOutQuad)
    location_state = location


def key_down(x):
    if x in down_keys.keys():
        return
    down_keys[x] = True
    pyautogui.keyDown(x)


def key_up(x):
    if x not in down_keys.keys():
        return
    del down_keys[x]
    pyautogui.keyUp(x)


def all_keys_up():
    for k in down_keys.keys():
        pyautogui.keyUp(k)
    down_keys.clear()


def copy_item_at_cursor():
    key_down('ctrl')
    sleep(KEY_PRESS_DELAY)
    key_down('altleft')
    sleep(KEY_PRESS_DELAY)
    pyautogui.press('c')
    sleep(KEY_PRESS_DELAY)
    key_up('altleft')
    sleep(KEY_PRESS_DELAY)
    key_up('ctrl')


def use_picked_up_currency_on_stash_item(currency):
    print('[Debug] Using', currency, ' on item')
    move_mouse(ITEM_LOCATION)
    key_down('shift')
    if not DEBUG_MODE:
        pyautogui.click(button='left')
    sleep(KEY_PRESS_DELAY)
    currency_state[currency] = currency_state[currency] - 1


def pickup_currency(currency):
    print("[Debug] Picking up currency: ", currency)
    print("[Debug] Currency state: ", currency_state)
    if currency_state['picked_up_currency'] == currency:
        # Currency already picked up.
        return
    elif currency_state['picked_up_currency'] != currency or currency_state[
        'picked_up_currency'] is None:
        # Remove picked up state by un holding shift
        key_up('shift')
        currency_state['picked_up_currency'] = None

    move_mouse(CURRENCY_LOCATION[currency])

    if currency_state[currency] is None:
        copy_item_at_cursor()
        parse_currency_from_clipboard()

    if currency_state[currency] <= 0:
        raise Exception("OutOfCurrencyException")

    pyautogui.click(button='right')
    currency_state['picked_up_currency'] = currency


def use_currency_on_item(currency):
    if currency_state['picked_up_currency'] != currency:
        pickup_currency(currency)
    if currency_state[currency] <= 0:
        raise Exception("OutOfCurrencyException")
    use_picked_up_currency_on_stash_item(currency)


def should_use_augment():
    # Remove
    # return False
    if magic_mod_check(item_state, required_state):
        return False

    for mod in required_state['magic_mods']:
        if should_use_augment_single_mod(item_state, mod):
            return True
    return False


def should_use_augment_single_mod(item_state, required_mod):
    print("[Debug] should_use_augment_single_mod, item_state :", item_state)

    item_nmods = 0
    required_nmods = 0

    if item_state['mods']['prefix']:
        item_nmods = item_nmods + 1
    if item_state['mods']['suffix']:
        item_nmods = item_nmods + 1

    if item_nmods > 1:
        return False

    if required_mod['prefix']:
        required_nmods = required_nmods + 1
    if required_mod['suffix']:
        required_nmods = required_nmods + 1

    if required_nmods > 1:
        # Item has both prefix and suffix required. Check if both match.
        if not prefix_match(item_state, required_mod) or not suffix_match(
                item_state, required_mod):
            return False
        return True

    elif required_nmods == 1:
        m = 'prefix'
        if not required_mod[m]:
            m = 'suffix'
        if not item_state['mods'][m]:
            return True
        return False
    return False


def convert_to_rare():
    use_currency_on_item('Regal Orb')


def move_item_to_inventory():
    all_keys_up()
    key_down('ctrl')
    sleep(KEY_PRESS_DELAY)
    pyautogui.click(button='left')
    key_up('ctrl')


def move_item_to_stash(n):
    all_keys_up()
    print("[Debug] Moving item {} to stash".format(n))
    r, c = required_state['inventory_positions'][n]
    location = get_location_for_inventory_position(r, c)
    move_mouse(location)
    key_down('ctrl')
    sleep(KEY_PRESS_DELAY)
    pyautogui.click(button='left')
    key_up('ctrl')


def roll():
    if item_state['rarity'] == 'normal':
        use_currency_on_item('orb of transmutation')
        item_state['rarity'] = 'magic'
        read_item_rolls()

    if magic_mod_check(item_state, required_state):
        return

    use_currency_on_item('orb of alteration')
    read_item_rolls()
    if should_use_augment():
        use_currency_on_item('orb of augmentation')
        read_item_rolls()


def start_rolling():
    global flog
    print("Starting rolling ...")
    move_mouse(ITEM_LOCATION)
    n_rolls = 0

    # Read initial item rolls
    read_item_rolls()
    if item_state['rarity'] == 'rare':
        if rare_mod_check(item_state, required_state):
            print("[Success] Item rolled successfully !")
            move_item_to_inventory()
            return
        else:
            use_currency_on_item('orb of scouring')
            read_item_rolls()

    while n_rolls < MAX_ROLLS:
        print("\n\nRoll ({})............................".format(n_rolls))
        try:
            if magic_mod_check(item_state, required_state):
                if item_state['rarity'] == 'rare':
                    convert_to_rare()
                    read_item_rolls()
                    if rare_mod_check(item_state, required_state):
                        print("[Success] Item rolled successfully !")
                        move_item_to_inventory()
                        break
                    else:
                        print("Regal failed !")
                        use_currency_on_item('orb of scouring')
                        read_item_rolls()
                else:
                    print("[Success] Item rolled successfully !")
                    move_item_to_inventory()
                    return

            # Roll otherwise
            roll()
            sleep(ROLL_DELAY)
            n_rolls = n_rolls + 1
            flog.write(json.dumps(item_state) + "\n")
        except Exception as e:
            log("[Error] Exception in roll ")
            print("[Error] Exception in roll", e)
            flog.close()
            all_keys_up()
            raise e
    all_keys_up()
    flog.close()


def get_location_for_inventory_position(row, col):
    location = INVENTORY_00
    x = location[0] + col * INVENTORY_SLOT_SIZE
    y = location[1] + row * INVENTORY_SLOT_SIZE
    return x, y, x, y


def draw_location(location):
    x1, y1, x2, y2 = location
    win = Window(size=(x2 - x1, y2 - y1),
                 position=(x1, y1), alpha=1, draggable=False)
    label = tk.Label(win.root, text="Window_0")
    label.pack()
    Window.launch()
    # win.show()


def parse_magic_mods(magic_mods):
    required_mods = []
    for mod_option in magic_mods:
        required_mod = {
            "prefix": "",
            "suffix": "",
            "prefix_tier": "",
            "suffix_tier": ""
        }
        if mod_option['prefix']:
            required_mod['prefix'] = mod_option['prefix'].strip().lower()
        if mod_option['suffix']:
            required_mod['suffix'] = mod_option['suffix'].strip().lower()
        if mod_option['prefix_tier']:
            required_mod['prefix_tier'] = mod_option['prefix_tier']
        if mod_option['suffix_tier']:
            required_mod['suffix_tier'] = mod_option['suffix_tier']
        if not required_mod['prefix'] and not required_mod['suffix']:
            raise Exception("Invalid mod config !")
        required_mods.append(required_mod)
    return required_mods


def parse_rare_mods(rare_mods):
    required_mods = []
    for mod_option in rare_mods:
        mod_option = mod_option.strip().lower()
        required_mods.append(mod_option)
    return required_mods


def sanitize_config_and_read():
    required_state = {}

    f = open(AFFIX_FILE)
    data = json.load(f)
    f.close()

    required_state['base_name'] = data['base_name'].strip().lower()
    print("[Debug] Item base_name =", required_state['base_name'])

    required_state['num_items'] = int(data['num_items'])
    required_state['inventory_positions'] = data['inventory_positions']
    if len(required_state['inventory_positions']) < required_state[
        'num_items']:
        raise Exception("Inventory locations not provided for all items !")

    data = data['required_state']
    if data['rarity'] not in SUPPORTED_RARITIES:
        raise Exception("Rarity not supported !")

    if data['rarity'] == 'rare' and not data['rare_mods']:
        raise Exception("Missing rare_mods field in required_state !")

    required_state['magic_mods'] = parse_magic_mods(data['magic_mods'])
    required_state['rare_mods'] = parse_rare_mods(data['rare_mods'])

    print("[Debug] Preprocessed required: ", pformat(required_state))
    print("[Debug] item: ", pformat(item_state))
    return required_state


def preprocess_config():
    global required_state
    required_state = sanitize_config_and_read()


def run_timer():
    input("Press enter to confirm ...")
    t = 5
    for i in range(0, 5):
        time.sleep(1)
        print("Move to POE..({})".format(t - i))


def reset():
    global item_state
    global currency_state
    global location_state
    item_state = {
        "rarity": "normal",
        "mods": {
            "prefix": None,
            "suffix": None
        }
    }
    currency_state = {'picked_up_currency': None}
    for k in CURRENCY_LOCATION.keys():
        currency_state[k] = None
    location_state = None


################################################################################
# Start rolling the item.
print("Rolling with ", AFFIX_FILE)
flog = open(LOG_FILE, "a+")

# Preprocessing
preprocess_config()
run_timer()

for i in range(0, required_state['num_items']):
    print("[Debug] Rolling item number: ", pformat(i))
    reset()
    move_item_to_stash(i)
    start_rolling()
