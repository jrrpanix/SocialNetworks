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
        self.O, self.H, self.L, self.C, self.V, self.T, self.ts0, self.ts = None, 0, 0, 0, 0, 0, None, None

    def update(self, dt0, dt, p, q):
        if self.O is None:
            self.O, self.H, self.L, self.C, self.V = p, p, p, p, q
            if q > 0 : self.T = 1
            self.ts0 = dt0
            self.ts = dt
        else:
            self.C = p
            if q > 0 : self.T += 1
            self.V += q
            if p < self.L : self.L = p
            if p > self.H : self.H = p
            self.ts = dt

    def __str__(self):
        return ("%s,%f,%f,%f,%f,%d,%f") % (str(self.ts0),self.O, self.H, self.L, self.C, self.T, self.V)

class Interval :
    
    def __init__(self, start, delta=datetime.timedelta(seconds=1)):
        self.start = start
        self.next = start + delta
        self.begin, self.end, self.delta, self.ohlc, self.hist = None, None, delta, None, []

    def update(self, dt, p, q):
        if dt < self.next:
            if self.ohlc is None : self.ohlc = OHLC()
            self.ohlc.update(self.start, dt, p, q)
        else:
            self.next_start(dt)
            if self.ohlc is not None:
                self.hist.append(self.ohlc)
            self.ohlc = OHLC()
            self.ohlc.update(self.start, dt, p, q)

    def next_start(self, dt):
        while self.next < dt:
            self.start = self.next
            self.next = self.next + self.delta

    def sortByMax(self):
        return sorted(self.hist, key = lambda x : x.H - x.L, reverse=True)


class ProcessOHLC:

    def process(infile, outfile, startDT, stopDT, delta):
        intvl = Interval(startDT, delta)
        wrt = open(outfile, "w") 
        with gzip.open(infile) as rdr:
            for i, line in enumerate(rdr):
                if i == 0 : 
                    continue
                else:
                    data = Utils.parse(line)
                    dt = data[0]
                    if dt < startDT : continue
                    if dt > stopDT : break
                    intvl.update(data[0], data[1], data[2])
        for h in intvl.hist:
            wrt.write( "%s\n" % h)
        wrt.close()

def main():
    if len(sys.argv) < 3:
        print("Error : usage <tickFile.csv.gz> <timeDeltaSeconds>")
        quit()
    infile, deltaSec = sys.argv[1], int(sys.argv[2])
    if len(sys.argv) == 4:
        outfile = sys.argv[3]
    else:
        outfile = "./%s_OHLC_%d.csv" % (os.path.basename(infile).split(".")[0], deltaSec)
    assert os.path.exists(infile)
    start, stop, delta = Utils.DT(2018,1,2,6,0,0), Utils.DT(2019, 3, 15, 7, 0, 0), datetime.timedelta(seconds=deltaSec)
    ProcessOHLC.process(infile, outfile, start, stop, delta)

if __name__ == '__main__':
    main()
