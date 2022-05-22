import json
import logging
import time

import requests

from siosa.common.singleton import Singleton

TRADE_PAGE = "https://www.pathofexile.com/trade/search/{}/"
SEARCH_API = "https://www.pathofexile.com/api/trade/search/{}"
EXCHANGE_API = "https://www.pathofexile.com/api/trade/exchange/{}"
FETCH_API = "https://www.pathofexile.com/api/trade/fetch/"
STATIC_DATA_API = "https://www.pathofexile.com/api/trade/data/static"
STASH_INFO_API = "https://www.pathofexile.com/character-window/get-stash-items?accountName={}&realm=pc&league={}&tabs=1"
CHARACTER_LIST_API = "https://www.pathofexile.com/character-window/get-characters?accountName={}"
PROFILE_API = "https://api.pathofexile.com/profile"
LEAGUE_API = "https://api.pathofexile.com/leagues"
SCRAPE_STR1 = 'require(["main"], function(){require(["trade"], function(t){    t('
SCRAPE_STR2 = ');});});'
USER_AGENT = 'Mozilla/5.0'
MAX_ITEMS_FOR_CALCULATING_EXCHANGE = 30
STASH_METADATA_REFRESH_DELAY = 30


class PoeApi(metaclass=Singleton):
    # Cache for static methods.
    CHARACTERS_FOR_ACCOUNT_NAME = {}
    LEAGUES = None
    PROFILE = {}

    def __init__(self, account_name, poe_session_id, league):
        """
        Args:
            config: SiosaConfig
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')
        self.account_name = account_name
        self.poe_session_id = poe_session_id
        self.league = league
        self.stash_metadata = None
        self.stash_metadata_fetch_ts = None
        self.cookies = {'POESESSID': poe_session_id}
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'POESESSID': poe_session_id,
            'user-agent': USER_AGENT
        }

    def get_stash_metadata(self, refresh=True):
        if not refresh and self.stash_metadata and \
                time.time() - self.stash_metadata_fetch_ts <= \
                STASH_METADATA_REFRESH_DELAY:
            return self.stash_metadata

        url = STASH_INFO_API.format(self.account_name, self.league)
        resp = requests.get(url, headers=self.headers, cookies=self.cookies)
        if not resp.content:
            return {}

        data = json.loads(resp.content)
        if 'error' in data or 'tabs' not in data:
            return {}

        self.stash_metadata = data
        self.stash_metadata_fetch_ts = time.time()
        self.logger.debug("Got stash metadata. Number of tabs: {}".format(
            len(data['tabs'])))
        return data

    def get_stash_contents(self, index):
        """
        Args:
            index:
        """
        url = STASH_INFO_API.format(self.account_name, self.league) \
              + "&tabIndex=" + str(index)
        resp = requests.get(url, headers=self.headers, cookies=self.cookies)
        if not resp.content:
            return
        contents = json.loads(resp.content)
        self.logger.debug(
            "Got stash contents for index({}): items={}".format(
                index, len(contents['items'])))
        return contents['items']

    def get_all_trades(self, url):
        # Request
        """
        Args:
            url:
        """
        page_response = requests.get(url, headers=self.headers,
                                     cookies=self.cookies)
        if not page_response.content:
            return

        index1 = page_response.content.find(SCRAPE_STR1) + len(SCRAPE_STR1)
        index2 = page_response.content.find(SCRAPE_STR2)
        j = json.loads(page_response.content[index1: index2])['state']
        search_request = {
            'query': j,
            'sort': {
                'price': 'asc'
            }
        }
        self.logger.debug(
            "Search request to get all trades for account: {}".format(
                json.dumps(search_request)))
        search_response = requests.post(
            self._get_league_specific_url(SEARCH_API), json=search_request,
            cookies=self.cookies, headers=self.headers)
        search_response = search_response.json()
        items = self._items_search(
            search_response['id'], search_response['result'])
        self.logger.debug("Got all trades for url({})".format(url))
        return items

    def _items_search(self, search_id, item_ids, exchange=False):
        # Search for items
        """
        Args:
            search_id:
            item_ids:
            exchange:
        """
        all_items = []
        for item_ids in PoeApi._divide_chunks(item_ids, 20):
            fetch_url = PoeApi.get_url_for_item_fetch(
                search_id, item_ids, exchange=exchange)

            # Some delay to prevent getting throttled.
            time.sleep(0.25)
            items = self.fetch_items_from_url(fetch_url)
            all_items.extend(items)
        return all_items

    @staticmethod
    def _divide_chunks(arr, c):
        # looping till length l
        """
        Args:
            arr:
            c:
        """
        for i in range(0, len(arr), c):
            yield arr[i:i + c]

    @classmethod
    def get_url_for_item_fetch(cls, search_id, item_ids, exchange):
        """
        Args:
            search_id:
            item_ids:
            exchange:
        """
        url = FETCH_API
        for item_id in item_ids:
            url = url + item_id['id'] + ","
        url = url[:-1]
        url = url + "?query=" + search_id
        if exchange:
            url = url + "&exchange"
        return url

    def fetch_items_from_url(self, url):
        """
        Args:
            url:
        """
        items_response = requests.get(url, headers=self.headers,
                                      cookies=self.cookies)
        return items_response.json()['result']

    def get_exchange_rate(self, have, want):
        """
        Args:
            have:
            want:
        """
        if not have or not want:
            return None
        data = {
            'query': {
                'status': {
                    'option': 'online'
                },
                'want': [want],
                'have': [have]
            },
            'engine': 'new'
        }
        self.logger.debug(
            "Getting exchanges for want({}), have({})".format(want, have))
        response = requests.post(
            self._get_league_specific_url(EXCHANGE_API), json=data,
            cookies=self.cookies, headers=self.headers)
        if not response.ok:
            self.logger.error(
                "Couldn't get exchanges for want({}), have({})".format(
                    want, have))
            return None
        response = response.json()
        items = self._items_search(
            response['id'],
            list(response['result'].values())[3:MAX_ITEMS_FOR_CALCULATING_EXCHANGE],
            exchange=True)
        try:
            rate = self._get_exchange_rate_from_exchange_entries(items)
        except Exception as e:
            self.logger.error(
                "Error getting exchange rate for want({}), have({})".format(
                    want, have))
            raise e
        self.logger.debug(
            "Getting exchanges for want({}), have({}): {}".format(
                want, have, rate))
        return rate

    def _get_exchange_rate_from_exchange_entries(self, items):
        """
        Args:
            items:
        """
        if not items:
            return None
        exchanges = items[3:MAX_ITEMS_FOR_CALCULATING_EXCHANGE]
        prices = []
        for exchange in exchanges:
            have_amount = exchange['listing']['price']['exchange']['amount']
            want_amount = exchange['listing']['price']['item']['amount']
            prices.append(want_amount * 1.0 / have_amount)
        return sum(prices) / len(prices)

    def get_static_data(self):
        url = STATIC_DATA_API
        resp = requests.get(url, headers=self.headers,
                            cookies=self.cookies).json()
        if not resp or not resp['result']:
            return
        self.logger.debug(
            "Got static data len=({}) ".format(len(resp['result'])))
        return resp['result']

    def _get_league_specific_url(self, url):
        """
        Args:
            url:
        """
        return url.format(self.league)

    @staticmethod
    def get_characters(account_name):
        if not account_name:
            return []

        if account_name in PoeApi.CHARACTERS_FOR_ACCOUNT_NAME:
            characters = PoeApi.CHARACTERS_FOR_ACCOUNT_NAME.get(account_name)
            if time.time() - characters['ts'] <= 60 * 60:
                # One hour
                return characters['characters']

        url = CHARACTER_LIST_API.format(account_name)
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'user-agent': USER_AGENT
        }
        resp = requests.get(url, headers=headers)
        try:
            characters = resp.json()
            if 'error' not in characters:
                PoeApi.CHARACTERS_FOR_ACCOUNT_NAME[account_name] = {
                    'ts': time.time(),
                    'characters': characters
                }
                return characters
            return []
        except:
            return []

    @staticmethod
    def get_profile(poe_ssid):
        if poe_ssid in PoeApi.PROFILE:
            return PoeApi.PROFILE[poe_ssid]

        if not poe_ssid:
            return {}

        cookies = {'POESESSID': poe_ssid}
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'POESESSID': poe_ssid,
            'user-agent': USER_AGENT
        }
        resp = requests.get(PROFILE_API, headers=headers, cookies=cookies)
        try:
            PoeApi.PROFILE[poe_ssid] = resp.json()
            return PoeApi.PROFILE[poe_ssid]
        except:
            return {}

    @staticmethod
    def get_leagues():
        if PoeApi.LEAGUES:
            return PoeApi.LEAGUES

        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'user-agent': USER_AGENT
        }
        resp = requests.get(LEAGUE_API, headers=headers)
        try:
            PoeApi.LEAGUES = resp.json()
            return PoeApi.LEAGUES
        except:
            return []
