# Python 3.6
import gzip
import csv
from datetime import datetime, timedelta, timezone
from collections import deque

class Announcement:
    def __init__(self, csvline):
        self.datetime, self.currency, self.title, self.priority, self.actual, self.forecast, self.previous = datetime.strptime(csvline[0], '%Y-%m-%dT%H:%M:%S').astimezone(timezone.utc),csvline[1],csvline[2],csvline[3],csvline[4],csvline[5],csvline[6]    

class OHLC:
    def __init__(self, ts0, O, H, L, C, T, V, ts=None):
        self.ts0, self.O, self.H, self.L, self.C, self.T, self.V, self.ts = ts0, O, H, L, C, T, V, ts
        if self.ts is None : self.ts = self.ts0

    def __str__(self):
        return ("%s,%10.6f,%10.6f,%10.6f,%10.6f,%6d,%6d") % (str(self.ts0),self.O, self.H, self.L, self.C, self.T, int(self.V))


def group(events, records, before_min:int, after_min:int):
    bfdelta = timedelta(minutes=before_min)
    afdelta = timedelta(minutes=after_min)
    before = deque()
    after = deque()
    try:
        nxt = next(records)
        for ev in events:
            before_time = ev.datetime - bfdelta
            after_time = ev.datetime + afdelta

            while nxt.ts < before_time:
                nxt = next(records)
            try:
                while nxt.ts <= after_time:
                    after.append(nxt)
                    nxt = next(records)
            except StopIteration:
                pass
            
            while before and before[0].ts < before_time:
                before.popleft()
            while after and after[0].ts < ev.datetime:
                before.append(after.popleft())

            yield (ev, before, after)
    except StopIteration:
        pass
    

def record_reader(path):
    tz = timezone(timedelta(hours=-5))
    with gzip.open(path, 'rt') as rdr:
        for line in csv.reader(rdr):
            line[0] = datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S').astimezone(tz)
            line[1:5] = [float(x) for x in line[1:5]]
            line[5],line[6] = int(line[5]), int(line[6][:line[6].find('.')])
            yield OHLC(line[0],line[1],line[2],line[3],line[4],line[5],line[6])

def event_reader(path):
    with open(path, encoding='utf-8') as f:
        for event in csv.reader(f):
            yield Announcement(event)
