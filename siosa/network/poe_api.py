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
SCRAPE_STR1 = 'require(["main"], function(){require(["trade"], function(t){    t('
SCRAPE_STR2 = ');});});'
USER_AGENT = 'Mozilla/5.0'
MAX_ITEMS_FOR_CALCULATING_EXCHANGE = 20


class PoeApi(metaclass=Singleton):
    def __init__(self, account_name, poe_session_id, league="Ultimatum"):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel('DEBUG')

        self.account_name = account_name
        self.league = league
        self.session_id = poe_session_id
        self.cookies = {'POESESSID': self.session_id}
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'POESESSID': self.session_id,
            'user-agent': USER_AGENT
        }

    def get_stash_metadata(self):
        url = STASH_INFO_API.format(self.account_name, self.league)
        resp = requests.get(url, headers=self.headers, cookies=self.cookies)
        if not resp.content:
            return
        data = json.loads(resp.content)
        self.logger.debug("Got stash metadata. Number of tabs: {}".format(
            len(data['tabs'])))
        return data

    def get_stash_contents(self, index):
        url = STASH_INFO_API.format(
            self.account_name, self.league) + "&tabIndex=" + str(index)
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
        page_response = requests.get(url, headers=self.headers, cookies=self.cookies)
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
        headers = {
            'Content-type': 'application/json',
            'Accept': 'text/plain',
            'user-agent': USER_AGENT
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
        for i in range(0, len(arr), c):
            yield arr[i:i + c]

    @classmethod
    def get_url_for_item_fetch(cls, search_id, item_ids, exchange):
        url = FETCH_API
        for item_id in item_ids:
            url = url + item_id + ","
        url = url[:-1]
        url = url + "?query=" + search_id
        if exchange:
            url = url + "&exchange"
        return url

    def fetch_items_from_url(self, url):
        items_response = requests.get(url, headers=self.headers, cookies=self.cookies)
        return items_response.json()['result']

    def get_exchange_rate(self, have, want):
        if not have or not want:
            return None
        data = {
            'exchange': {
                'status': {
                    'option': 'online'
                },
                'want': [want],
                'have': [have]
            }
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
            response['result'][3:MAX_ITEMS_FOR_CALCULATING_EXCHANGE],
            exchange=True)
        rate = self._get_exchange_rate_from_exchange_entries(have, want, items)
        self.logger.debug(
            "Getting exchanges for want({}), have({}): {}".format(
                want, have, rate))
        return rate

    def _get_exchange_rate_from_exchange_entries(self, have, want, items):
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
        resp = requests.get(url, headers=self.headers, cookies=self.cookies).json()
        if not resp or not resp['result']:
            return
        self.logger.debug(
            "Got static data len=({}) ".format(len(resp['result'])))
        return resp['result']

    def _get_league_specific_url(self, url):
        return url.format(self.league)
