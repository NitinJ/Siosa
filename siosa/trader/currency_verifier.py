import logging
import math

from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.poe_currencies import Currency, CurrencyStack
from siosa.data.poe_item import ItemType
from siosa.network.poe_api import PoeApi


class CurrencyVerifier:
    SUPPORTED_CURRENCY_TYPES = ['chaos', 'exalted']
    ALLOWED_CHAOS_DIFF = 1.0

    def __init__(
            self,
            required_currency,
            support_exalted_as_chaos=False):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.support_exalted_as_chaos = support_exalted_as_chaos
        self.required_currency = required_currency
        self.exalted_ratio = None
        self.required_currencies = self._get_required_currencies()

    def _get_required_currencies(self):
        ctype = self.required_currency['type']
        amount = self.required_currency['amount']
        rcurrencies = {
            'chaos': 0,
            'exalted': 0
        }
        if float.is_integer(amount):
            amount = int(amount)
            rcurrencies[ctype] = amount
        else:
            assert ctype == 'exalted'
            ex_amount = int(amount)
            chaos_amount = (amount - ex_amount) * self._get_ex_to_chaos()
            rcurrencies['exalted'] = ex_amount
            rcurrencies['chaos'] = chaos_amount
        return rcurrencies

    def _get_currency_totals(self, items):
        currency = {
            'chaos': 0,
            'exalted': 0
        }
        for item in items:
            if item.type and item.type != ItemType.CURRENCY:
                raise Exception("Non currency item.")

            if item.currency.trade_name not in \
                    CurrencyVerifier.SUPPORTED_CURRENCY_TYPES:
                raise Exception("Unsupported currency")

            currency_type = item.currency.trade_name
            amount = item.quantity
            currency[currency_type] = currency[currency_type] + amount
        self.logger.debug("Got currency : {}".format(currency))
        return currency

    def _get_ex_to_chaos(self):
        if self.exalted_ratio:
            return self.exalted_ratio
        exalted = Currency(CurrencyExchange(), 'Exalted orb', 'exalted', 10)
        self.exalted_ratio = math.floor(exalted.get_value_in_chaos())
        self.logger.debug("Got chaos-ex ratio: {}".format(self.exalted_ratio))
        return self.exalted_ratio

    def verify(self, items):
        try:
            currency = self._get_currency_totals(items)
            required_currencies = self._get_required_currencies()
            self.logger.debug(
                "Required currency: {}, Got currency: {}".format(
                    required_currencies, currency))
            if not self.support_exalted_as_chaos:
                # Exact match.
                exalted_match = currency['exalted'] == required_currencies[
                    'exalted']
                chaos_diff = (required_currencies['chaos'] - currency['chaos'])
                return {
                    'verified': (exalted_match and
                                 chaos_diff <= CurrencyVerifier.ALLOWED_CHAOS_DIFF),
                    'missing_ex': not exalted_match,
                    'missing_chaos': (chaos_diff)
                }
            else:
                # Chaos match.
                chaos = self.get_chaos(currency)
                required_chaos = self.get_chaos(required_currencies)
                chaos_diff = required_chaos - chaos
                return {
                    'verified': (
                                chaos_diff <= CurrencyVerifier.ALLOWED_CHAOS_DIFF),
                    'missing_ex': False,
                    'missing_chaos': chaos_diff
                }
        except:
            return False

    def get_chaos(self, currency):
        return currency['exalted'] * self._get_ex_to_chaos() + currency['chaos']


if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT)

    exchange = CurrencyExchange(
        PoeApi("MopedDriverr", "2561bcd7ed51683282115e110e6ea1f3"))
    chaos = Currency(exchange, 'Chaos Orb', 'chaos', 10)
    exalted = Currency(exchange, 'Exalted Orb', 'exalted', 10)

    # Test 1
    currency = {
        'type': 'chaos',
        'amount': 25.0
    }
    cv = CurrencyVerifier(currency, support_exalted_as_chaos=False)
    assert True == cv.verify([
        CurrencyStack(chaos, 10),
        CurrencyStack(chaos, 10),
        CurrencyStack(chaos, 5)
    ])['verified']
    assert True == cv.verify([
        CurrencyStack(chaos, 10),
        CurrencyStack(chaos, 10),
        CurrencyStack(chaos, 4)
    ])['verified']
    assert False == cv.verify([
        CurrencyStack(chaos, 10),
        CurrencyStack(chaos, 10)
    ])['verified']
    res = cv.verify([
        CurrencyStack(chaos, 10),
        CurrencyStack(chaos, 10)
    ])
    assert 5 == res['missing_chaos'], "Obtained value = %d" % (res['missing_chaos'])

    # Test 2
    currency = {
        'type': 'exalted',
        'amount': 2.0
    }
    cv = CurrencyVerifier(currency, support_exalted_as_chaos=False)
    assert True == cv.verify([
        CurrencyStack(exalted, 2)
    ])['verified']
    assert False == cv.verify([
        CurrencyStack(exalted, 1),
        CurrencyStack(chaos, 100)
    ])['verified']

    # Test 3
    currency = {
        'type': 'exalted',
        'amount': 2.5
    }
    cv = CurrencyVerifier(currency, support_exalted_as_chaos=False)
    assert True == cv.verify([
        CurrencyStack(exalted, 2),
        CurrencyStack(chaos, 50)
    ])['verified']
    assert False == cv.verify([
        CurrencyStack(exalted, 2),
        CurrencyStack(chaos, 45)
    ])['verified']

    # Test 4
    currency = {
        'type': 'exalted',
        'amount': 2.5
    }
    cv = CurrencyVerifier(currency, support_exalted_as_chaos=True)
    assert True == cv.verify([
        CurrencyStack(exalted, 2),
        CurrencyStack(chaos, 50)
    ])['verified']
    assert False == cv.verify([
        CurrencyStack(exalted, 2),
        CurrencyStack(chaos, 45)
    ])['verified']
    assert True == cv.verify([
        CurrencyStack(exalted, 0),
        CurrencyStack(chaos, 250)
    ])['verified']

    # Test 5
    currency = {
        'type': 'exalted',
        'amount': 2.4
    }
    cv = CurrencyVerifier(currency, support_exalted_as_chaos=True)
    assert True == cv.verify([
        CurrencyStack(exalted, 2),
        CurrencyStack(chaos, 39)
    ])['verified']

    print("All tests passed")
