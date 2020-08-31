import threading
import time

import pyautogui

from siosa.control.game_step import Step


# pyautogui.FAILSAFE = False

def click(index, stops):
    print('Click called @', time.time())
    pyautogui.click()
    pos = pyautogui.position()
    print('Clicking at: ', pos)
    print('Diff: ', pos[1] - stops[index])
    print('Click done at: ', time.time())
    print()


class setInterval:
    def __init__(self, interval, action, ev, stops):
        self.interval = interval
        self.action = action
        self.ev = ev
        self.stops = stops
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        print('Waiting on event: ', time.time())
        self.ev.wait()
        print('Starting...', time.time())
        print()
        nextTime = time.time() + self.interval
        click_index = 0
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action(click_index, self.stops)
            click_index += 1

    def cancel(self):
        self.stopEvent.set()


class TestStep(Step):
    def __init__(self):
        Step.__init__(self)

    def execute(self, game_state):
        X = 960
        Y1 = 0
        Y2 = 1080
        T = 1
        D = Y2 - Y1
        S = D * 1.0 / T
        interval = 0.2

        stops = []
        s = 0
        while s <= D:
            s += S * interval
            stops.append(s)

        ts = time.time()
        print('Moving to: y{} on time({})'.format(Y1, ts))
        pyautogui.moveTo(X, Y1, 0.2)
        print('Moved to: y{}, Diff: {}'.format(Y1, time.time() - ts - 0.2))
        time.sleep(1)

        # start action every Xs
        ev = threading.Event()
        clicker = setInterval(interval, click, ev, stops)

        ev.set()
        pyautogui.moveTo(X, D, T, pyautogui.linear)

        clicker.cancel()
