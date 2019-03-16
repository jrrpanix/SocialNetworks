import gzip
import sys
import os
import binascii
import datetime

"""
 Social Networks Class Project
 Detecting Cheating in Economic Announcements
 Author : John Reynolds
 Date : 3.16.2019
"""
class Utils:

    def roundDT(d):
        return datetime.datetime(d.year, d.month, d.day, d.hour, d.minute, d.second, 0)

    def DT(year, month, day, hour, minute, second):
        return datetime.datetime(year, month, day, hour, minute, second, 0)

    def getDT(d, t, micros=True):
        dv, tv = d.split("/"), t.split(":")
        try:
            h, m, s = int(tv[0]), int(tv[1]), int(tv[2].split(".")[0])
            us = 0 if micros == False else int(tv[2].split(".")[-1])*1000
        except:
            print("Error parsing datetime time=%s, date=%s" % (t, d))
            return datetime.datetime(2018,1,1)
        return datetime.datetime(int(dv[2]), int(dv[0]), int(dv[1]), h,m,s,us)

    def parse(line):
        # trades data : date, time, price, qty, flag -> datetime, price , qty
        if type(line) != str: line = line.decode("ascii")
        dv = line.strip().split(",")
        return (Utils.getDT(dv[0], dv[1]), float(dv[2]), float(dv[3]))

class OHLC:

    def __init__(self):
        self.O, self.H, self.L, self.C, self.V, self.T, self.ts = None, 0, 0, 0, 0, 0, None

    def update(self, dt, p, q):
        if self.O is None:
            self.O, self.H, self.L, self.C, self.V = p, p, p, p, q
            if q > 0 : self.T = 1
            self.ts = dt
        else:
            self.C = p
            if q > 0 : self.T += 1
            self.V += q
            if p < self.L : self.L = p
            if p > self.H : self.H = p

    def __str__(self):
        return ("%s,%f,%f,%f,%f,%d,%f") % (str(self.ts),self.O, self.H, self.L, self.C, self.T, self.V)

class Interval :
    
    def __init__(self, delta=datetime.timedelta(seconds=1)):
        self.begin, self.end, self.delta, self.ohlc, self.hist = None, None, delta, None, []

    def update(self, dt, p, q):
        if self.end is None or dt > self.end:
            self.begin = Utils.roundDT(dt)
            self.end = self.begin + self.delta
            print(self.begin, self.end)
            if self.ohlc is not None:
                self.hist.append(self.ohlc)
            self.ohlc = OHLC()
        self.ohlc.update(self.begin, p, q)

def readerV1(fname, startDT, stopDT, delta):
    
    intvl = Interval(delta)
    with gzip.open(fname) as fr:
        for i, line in enumerate(fr):
            if i == 0 : 
                continue
            else:
                data = Utils.parse(line)
                dt = data[0]
                if dt < startDT : continue
                if dt > stopDT : break
                intvl.update(data[0], data[1], data[2])
    print(len(intvl.hist))
    print(intvl.hist[0])
    print(intvl.hist[1])
    print(intvl.hist[2])
    print(intvl.hist[-3])
    print(intvl.hist[-2])
    print(intvl.hist[-1])

def main():
    fname="~/eod/tick/csv/UB.csv.gz" if len(sys.argv) == 1 else sys.argv[1]
    assert os.path.exists(fname)
    readerV1(fname, Utils.DT(2018,1,2,6,0,0), Utils.DT(2018, 1, 2, 6, 3, 0), datetime.timedelta(seconds=30))

if __name__ == '__main__':
    main()
