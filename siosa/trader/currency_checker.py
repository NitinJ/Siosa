import logging
import math

from siosa.data.currency_exchange import CurrencyExchange
from siosa.data.poe_currencies import Currency
from siosa.network.poe_api import PoeApi


class CurrencyChecker:
    """
    Class to calculate currency diffs between what is required for a trade and
    what was offered. Only supports chaos and exalted orbs at the moment.
    """
    SUPPORTED_CURRENCY_TYPES = ['chaos', 'exalted']

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

    def get_diffs(self, currency):
        """
        Calculates and returns currency diffs between trade request and
        currency offered.
        Args:
            currency: A dictionary of {currency_name: currency_count..}

        Returns: A dictionary of {currency_name: diff}
        """
        for c in CurrencyChecker.SUPPORTED_CURRENCY_TYPES:
            if c not in currency.keys():
                currency[c] = 0

        required = self._get_required_currencies()
        self.logger.debug(
            "Required currency: {}, Got currency: {}".format(
                required, currency))
        if not self.support_exalted_as_chaos:
            exalt_diff = currency['exalted'] - required['exalted']
            chaos_diff = currency['chaos'] - required['chaos']
            return {
                'chaos': math.floor(chaos_diff),
                'exalted': exalt_diff
            }
        else:
            # Chaos only match.
            chaos_diff = self._get_chaos(currency) - self._get_chaos(required)
            return {
                'chaos': math.floor(chaos_diff),
                'exalted': 0
            }

    def _get_chaos(self, currency):
        return currency['exalted'] * self._get_ex_to_chaos() + currency['chaos']

    def _get_required_currencies(self):
        currency_type = self.required_currency['type']
        amount = self.required_currency['amount']
        required_currencies = {
            'chaos': 0,
            'exalted': 0
        }
        if float.is_integer(amount):
            # This check is required because amounts are in the form: 30.0 chaos
            # or 2.0 exalted
            amount = int(amount)
            required_currencies[currency_type] = amount
        else:
            assert currency_type == 'exalted'
            ex_amount = int(amount)
            chaos_amount = (amount - ex_amount) * self._get_ex_to_chaos()
            required_currencies['exalted'] = ex_amount
            required_currencies['chaos'] = chaos_amount
        return required_currencies

    def _get_ex_to_chaos(self):
        if self.exalted_ratio:
            return self.exalted_ratio
        exalted = Currency(CurrencyExchange(), 'Exalted orb', 'exalted', 10)
        self.exalted_ratio = math.floor(exalted.get_value_in_chaos())
        self.logger.debug("Got chaos-ex ratio: {}".format(self.exalted_ratio))
        return self.exalted_ratio

if __name__ == "__main__":
    FORMAT = "%(created)f - %(thread)d: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    exchange = CurrencyExchange(
        PoeApi("MopedDriverr", "2561bcd7ed51683282115e110e6ea1f3"))

    # Patch currency verifier to take a fixed rate of 100c per ex.
    CurrencyChecker._get_ex_to_chaos = lambda x: 100

    # Test 1
    currency = {'type': 'chaos', 'amount': 25.0}
    cv = CurrencyChecker(currency, support_exalted_as_chaos=False)
    assert {'chaos': 0, 'exalted': 0} == \
           cv.get_diffs({'chaos': 25, 'exalted': 0})
    assert {'chaos': -1, 'exalted': 0} == \
           cv.get_diffs({'chaos': 24, 'exalted': 0})

    # Test 2
    currency = {'type': 'exalted', 'amount': 2.0}
    cv = CurrencyChecker(currency, support_exalted_as_chaos=False)
    assert {'chaos': 0, 'exalted': 0} == \
           cv.get_diffs({'chaos': 0, 'exalted': 2})
    assert {'chaos': 100, 'exalted': -1} == \
           cv.get_diffs({'chaos': 100, 'exalted': 1})

    # Test 3
    currency = {'type': 'exalted', 'amount': 2.5}
    cv = CurrencyChecker(currency, support_exalted_as_chaos=False)
    assert {'chaos': 0, 'exalted': 0} == \
           cv.get_diffs({'chaos': 50, 'exalted': 2})
    assert {'chaos': -5, 'exalted': 0} == \
           cv.get_diffs({'chaos': 45, 'exalted': 2})

    # Test 4
    currency = {'type': 'exalted', 'amount': 2.5}
    cv = CurrencyChecker(currency, support_exalted_as_chaos=True)
    assert {'chaos': 0, 'exalted': 0} == \
           cv.get_diffs({'chaos': 50, 'exalted': 2})
    assert {'chaos': -5, 'exalted': 0} == \
           cv.get_diffs({'chaos': 45, 'exalted': 2})
    assert {'chaos': 0, 'exalted': 0} == \
           cv.get_diffs({'chaos': 250, 'exalted': 0})

    # Test 5
    currency = {'type': 'exalted', 'amount': 2.4}
    cv = CurrencyChecker(currency, support_exalted_as_chaos=True)
    assert {'chaos': 10, 'exalted': 0} == \
           cv.get_diffs({'chaos': 250, 'exalted': 0})

    print("All tests passed")
