
def pascal_row(n):
    # This returns the nth row of Pascal's Triangle
    """
    Args:
        n:
    """
    result = [1]
    x, numerator = 1, n
    for denominator in range(1, n // 2 + 1):
        # print(numerator,denominator,x)
        x *= numerator
        x /= denominator
        result.append(x)
        numerator -= 1
    if n & 1 == 0:
        # n is even
        result.extend(reversed(result[:-1]))
    else:
        result.extend(reversed(result))
    return result


class BezierMouseController:
    def __init__(self, points, deviation=10, speed=5):
        """
        Args:
            points: An array of tuples (x, y). Locations on screen.
            deviation: Deviation from actual points in the bezier curve. 0 is 0%
                deviation
            speed: 1 is fastest
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.points = [p.get_center() for p in points]
        self.deviation = deviation
        self.speed = speed
        self.pyautogui_vars_backup = {
            'MINIMUM_DURATION': pyautogui.MINIMUM_DURATION,
            'MINIMUM_SLEEP': pyautogui.MINIMUM_SLEEP,
            'PAUSE': pyautogui.PAUSE
        }
        self.bezier_pts = \
            self.connected_bez(self.points, self.deviation, self.speed)

    def _update_pyautogui_vars(self, restore=False):
        """
        Args:
            restore:
        """
        if restore:
            pyautogui.MINIMUM_DURATION = self.pyautogui_vars_backup[
                'MINIMUM_DURATION']
            pyautogui.MINIMUM_SLEEP = self.pyautogui_vars_backup[
                'MINIMUM_SLEEP']
            pyautogui.PAUSE = self.pyautogui_vars_backup['PAUSE']
            return

        # Any duration less than this is rounded to 0.0 to instantly move the
        # mouse.
        pyautogui.MINIMUM_DURATION = 0.5
        # Minimal number of seconds to sleep between mouse moves.
        pyautogui.MINIMUM_SLEEP = 0
        # The number of seconds to pause after EVERY public function call.
        pyautogui.PAUSE = 0

    def move_mouse(self):
        self._update_pyautogui_vars()
        for p in self.bezier_pts:
            pyautogui.moveTo(p)
        self._update_pyautogui_vars(restore=True)

    def make_bezier(self, xys):
        # xys should be a sequence of 2-tuples (Bezier control points)
        """
        Args:
            xys:
        """
        n = len(xys)
        combinations = pascal_row(n - 1)

        def bezier(ts):
            # This uses the generalized formula for bezier curves
            # http://en.wikipedia.org/wiki/B%C3%A9zier_curve#Generalization
            result = []
            for t in ts:
                tpowers = (t ** i for i in range(n))
                upowers = reversed([(1 - t) ** i for i in range(n)])
                coefs = [c * a * b for c, a, b in
                         zip(combinations, tpowers, upowers)]
                result.append(
                    list(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in
                         zip(*xys)))
            return result

        return bezier

    def mouse_bez(self, init_pos, fin_pos, deviation, speed):
        """GENERATE BEZIER CURVE POINTS Takes init_pos and fin_pos as a 2-tuple
        representing xy coordinates

            variation is a 2-tuple representing the max distance from fin_pos of
            control point for x and y respectively speed is an int multiplier
            for speed. The lower, the faster. 1 is fastest.

        Args:
            init_pos:
            fin_pos:
            deviation:
            speed:
        """

        # time parameter
        ts = [t / (speed * 100.0) for t in range(speed * 101)]

        # bezier centre control points between (deviation / 2) and (deviaion) of travel distance, plus or minus at random
        control_1 = (init_pos[0] + choice((-1, 1)) * abs(
            ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(
            deviation / 2,
            deviation),
                     init_pos[1] + choice((-1, 1)) * abs(
                         ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(
                         deviation / 2, deviation)
                     )
        control_2 = (init_pos[0] + choice((-1, 1)) * abs(
            ceil(fin_pos[0]) - ceil(init_pos[0])) * 0.01 * randint(
            deviation / 2,
            deviation),
                     init_pos[1] + choice((-1, 1)) * abs(
                         ceil(fin_pos[1]) - ceil(init_pos[1])) * 0.01 * randint(
                         deviation / 2, deviation)
                     )

        xys = [init_pos, control_1, control_2, fin_pos]
        bezier = self.make_bezier(xys)
        points = bezier(ts)

        return points

    def connected_bez(self, coord_list, deviation, speed):
        """Connects all the coords in coord_list with bezier curve and returns
        all the points in new curve

        ARGUMENT: DEVIATION (INT)
            deviation controls how straight the lines drawn my the cursor are.
            Zero deviation gives straight lines Accuracy is a percentage of the
            displacement of the mouse from point A to B, which is given as
            maximum control point deviation. Naturally, deviation of 10 (10%)
            gives maximum control point deviation of 10% of magnitude of
            displacement of mouse from point A to B, and a minimum of 5%
            (deviation / 2)

        Args:
            coord_list:
            deviation:
            speed:
        """
        self.logger.debug("Generating bezier for: {}".format(coord_list))
        i = 1
        points = []

        while i < len(coord_list):
            points += self.mouse_bez(coord_list[i - 1], coord_list[i],
                                     deviation,
                                     speed)
            i += 1

        return points


if __name__ == "__main__":

    # Move the mouse over all items at once.
    BezierMouseController(pts).move_mouse()