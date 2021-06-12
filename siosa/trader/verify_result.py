class VerifyResult:
    ALLOWED_CHAOS_DIFF = -1.0
    ALLOWED_CHAOS_DIFF_AT = 10
    SHORT_MSG = "hey you are short by {} {}"
    EXTRA_MSG = "hey you've put in {} extra {}. please remove"

    def __init__(self, currency_diff, required):
        self.required = required
        self.diff = currency_diff
        self.verified = True
        self.missing_currency = None
        self.missing_amount = 0
        self._populate()

    def _populate(self):
        if 'exalted' in self.diff.keys() and self.diff['exalted'] != 0:
            self.verified = False
            self.missing_currency = 'exalted'
            self.missing_amount = self.diff['exalted']
            return
        if 'chaos' in self.diff.keys():
            # Discount 1c only above the ALLOWED_CHAOS_DIFF_AT threshold.
            if (self.required['chaos'] <= VerifyResult.ALLOWED_CHAOS_DIFF_AT and
                self.diff['chaos'] != 0) or \
                    self.diff['chaos'] < VerifyResult.ALLOWED_CHAOS_DIFF:
                self.verified = False
                self.missing_currency = 'chaos'
                self.missing_amount = self.diff['chaos']
                return

    def is_verified(self):
        return self.verified

    def get_msg(self):
        if not self.missing_currency:
            return ""
        if self.missing_amount < 0:
            return VerifyResult.SHORT_MSG.format(abs(self.missing_amount),
                                                 self.missing_currency)
        else:
            return VerifyResult.EXTRA_MSG.format(abs(self.missing_amount),
                                                 self.missing_currency)

    def __repr__(self):
        return "[{}, {}, {}]".format(
            self.verified, self.missing_currency, self.missing_amount)


if __name__ == "__main__":
    diff = {'chaos': 0, 'exalted': 0}
    required = {'chaos': 100, 'exalted': 0}
    v = VerifyResult(diff, required)
    assert True == v.is_verified()
    assert "" == v.get_msg(), v.get_msg()

    diff = {'chaos': -1, 'exalted': 0}
    required = {'chaos': 100, 'exalted': 0}
    v = VerifyResult(diff, required)
    assert True == v.is_verified()
    assert "" == v.get_msg(), v.get_msg()

    diff = {'chaos': -2, 'exalted': 0}
    required = {'chaos': 100, 'exalted': 0}
    v = VerifyResult(diff, required)
    assert False == v.is_verified()
    assert "hey you are short by 2 chaos" == v.get_msg(), v.get_msg()

    diff = {'chaos': -1, 'exalted': 0}
    required = {'chaos': 10, 'exalted': 0}
    v = VerifyResult(diff, required)
    assert False == v.is_verified()
    assert "hey you are short by 1 chaos" == v.get_msg(), v.get_msg()

    diff = {'chaos': 0, 'exalted': -1}
    required = {'chaos': 0, 'exalted': 2}
    v = VerifyResult(diff, required)
    assert False == v.is_verified()
    assert "hey you are short by 1 exalted" == v.get_msg(), v.get_msg()

    diff = {'chaos': 0, 'exalted': 1}
    required = {'chaos': 0, 'exalted': 2}
    v = VerifyResult(diff, required)
    assert False == v.is_verified()
    assert "hey you've put in 1 extra exalted. please remove" == v.get_msg(), v.get_msg()

    diff = {'chaos': 1, 'exalted': -1}
    required = {'chaos': 50, 'exalted': 2}
    v = VerifyResult(diff, required)
    assert False == v.is_verified()
    assert "hey you are short by 1 exalted" == v.get_msg(), v.get_msg()

    print("All tests passed !")
