import logging
import os
import time
import sys

import pygsheets as pygsheets
from pprint import pprint
import pygsheets
import pandas as pd
from siosa.client.log_listener import ClientLogListener

FORMAT = "%(created)f: [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()
logger.setLevel('DEBUG')


def diff_format(d):
    """
    Args:
        d:
    """
    minutes = int(d / 60)
    seconds = int(d - minutes * 60)
    return int(d)
    # return "{}:{}".format(minutes, seconds)


class Timing:
    def __init__(self, start_zone, end_zone):
        """
        Args:
            start_zone:
            end_zone:
        """
        self.start_time = time.time()
        self.last_zone = start_zone.lower()
        self.end_zone = end_zone.lower()

        # zone: [[start, end]]
        self.timings = {self.last_zone: [[self.start_time, -1]]}
        self.first = {self.last_zone: 0.0}

    def moved_to_zone(self, zone):
        """
        Args:
            zone:
        """
        if not zone:
            return False, None

        zone = zone.lower()
        if zone == self.last_zone:
            return False, None
        ts = time.time()

        # Change of zone so record end of last zone
        last_zone_last_entry = self.timings[self.last_zone][-1]
        last_zone_last_entry[1] = ts
        logger.debug("Completed zone {} in {} seconds".format(
            self.last_zone,
            diff_format(
                last_zone_last_entry[1] - last_zone_last_entry[0])))

        # Record the time for first time seeing this new zone.
        if zone not in self.first.keys():
            self.first[zone] = ts - self.start_time
            logger.debug("Reached zone: {} @: {} seconds".format(
                zone, diff_format(self.first[zone])))

        self.last_zone = zone
        if zone not in self.timings.keys():
            self.timings[zone] = []
        self.timings[zone].append([ts, -1])

        if zone == self.end_zone:
            data = self.end()
            return True, data

        return False, None

    def end(self):
        ts = time.time()
        if self.last_zone:
            last_zone_last_entry = self.timings[self.last_zone][-1]
            last_zone_last_entry[1] = ts

        # zone: {total time spent}
        data = {}
        for zone, times in self.timings.items():
            if zone not in data.keys():
                data[zone] = {}

            zone_total = 0
            for start_end in times:
                start = start_end[0]
                end = start_end[1]
                if end == -1:
                    continue
                zone_total = zone_total + (end - start)
            data[zone]['total'] = diff_format(zone_total)

        for zone, t in self.first.items():
            data[zone]['split'] = diff_format(t)

        return data


def get_next_run_id(wks):
    """
    Args:
        wks:
    """
    headers = wks.get_row(1, include_tailing_empty=False)
    enumerated_headers = list(enumerate(headers))
    if len(enumerated_headers) == 1:
        return 1
    return len(enumerated_headers)


def get_all_zones(wks):
    """
    Args:
        wks:
    """
    first_column = wks.get_col(1)
    # We are doing a python slice here to avoid
    # extracting the column names from the first row (keyword)
    first_column_data = first_column[1:]
    return first_column_data


def add_column_for_run(wks, run_data, timing_type):
    """
    Args:
        wks:
        run_data:
        timing_type:
    """
    run_id = get_next_run_id(wks)
    all_zones_from_sheet = get_all_zones(wks)
    times = [''] * len(all_zones_from_sheet)

    for i in range(0, len(all_zones_from_sheet)):
        zone = all_zones_from_sheet[i]
        if zone in run_data.keys():
            times[i] = run_data[zone][timing_type]

    times.insert(0, "R{}".format(run_id))
    wks.add_cols(1)
    insert_id = run_id + 1
    wks.update_col(insert_id, times)


def sheet_update(data):
    """
    Args:
        data:
    """
    client_file_abs_path = \
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     'path-of-exile-racing-e3233f61f9c9.json')
    # authorization
    gc = pygsheets.authorize(service_file=client_file_abs_path)

    # Create empty dataframe
    df = pd.DataFrame()
    sh = gc.open('Racing')

    # Select the sheets
    wks_splits = sh[0]
    wks_totals = sh[1]

    add_column_for_run(wks_splits, data, 'split')
    add_column_for_run(wks_totals, data, 'total')


def store_data(data):
    """
    Args:
        data:
    """
    print(data)
    r = input("Save run ?")
    if r.lower() == 'y':
        sheet_update(data)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Please provide name of the start and end zone !")
        sys.exit()

    sz = sys.argv[1]
    ez = sys.argv[2]
    logger.debug("Starting zone: {}, end zone: {}".format(sz, ez))

    log_listener = ClientLogListener()
    log_listener.start()
    location_change_event_queue = log_listener.location_change_event_queue

    # Start time stamp of the App.
    start_ts = time.time()
    logger.info("Timer started @: {}".format(start_ts))

    timing = Timing(sz, ez)
    if sz == ez:
        sys.exit()

    while True:
        if not location_change_event_queue.empty():
            current_zone = location_change_event_queue.get().zone_str
            reached_end, data = timing.moved_to_zone(current_zone)
            if reached_end:
                # Reached the end zone.
                store_data(data)
                break
        time.sleep(0.05)
    sys.exit()
