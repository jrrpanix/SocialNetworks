import gzip
import sys
import os
import binascii
import datetime
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

"""
 Social Networks Class Project
 Detecting Cheating in Economic Announcements
 Author : John Reynolds
 Date : 3.16.2019
"""

class OHLC:

    def __init__(self, ts0, O, H, L, C, T, V, ts=None):
        self.ts0, self.O, self.H, self.L, self.C, self.T, self.V, self.ts = ts0, O, H, L, C, T, V, ts
        if self.ts is None : self.ts = self.ts0

    def __str__(self):
        return ("%s,%10.6f,%10.6f,%10.6f,%10.6f,%6d,%6d") % (str(self.ts0),self.O, self.H, self.L, self.C, self.T, int(self.V))


class Utils:

    def DT(year, month, day, hour, minute, second):
        return datetime.datetime(year, month, day, hour, minute, second, 0)

    def getDT(d, t, micros=False):
        if "/" in d:
            dv = d.split("/")
            year, month, day = int(dv[2]), int(dv[0]), int(dv[1])
        else:
            dv = d.split("-")
            year, month, day = int(dv[0]), int(dv[1]), int(dv[2])
        tv =  t.split(":")
        try:
            h, m, s = int(tv[0]), int(tv[1]), int(tv[2].split(".")[0])
            us = 0 if micros == False else int(tv[2].split(".")[-1])*1000
        except:
            print("Error parsing datetime time=%s, date=%s" % (t, d))
            return datetime.datetime(2018,1,1)
        return datetime.datetime(year, month, day, h,m,s,us)

    def parse(line):
        # trades data : date, time, price, qty, flag -> datetime, price , qty
        if type(line) != str: line = line.decode("ascii")
        dv = line.strip().split(",")
        return OHLC(Utils.getDT(dv[0].split(" ")[0],dv[0].split(" ")[1]),
                    float(dv[1]), float(dv[2]), float(dv[3]),float(dv[4]),int(dv[5]),float(dv[6]))

class ReadOHLC:

    def read(infile):
        records=[]
        with gzip.open(infile) as rdr:
            for line in rdr:
                records.append(Utils.parse(line))
        return records



def sortByMax(hist):
    return sorted(hist, key = lambda x : x.H - x.L, reverse=True)

def getRecords(hist, start, end):
    rec = []
    for h in hist:
        if h.ts > end :
            break
        if h.ts >= start :
            rec.append(h)
    return rec

def plotRecords(hist, start, end):
    recs = getRecords(hist, start, end)
    dates = [r.ts for r in recs]
    for i,d in enumerate(dates):
        if d.hour == 7 and d.minute == 30 :
            found = i
            break
    valuesH = [(r.H) for r in recs]
    valuesL = [(r.L) for r in recs]
    minv = np.min(valuesL)
    maxv = np.max(valuesH)
    x = [i for i in range(len(valuesH))]
    #datex = matplotlib.dates.date2num(dates)
    x1 = [found-2, found-2]
    y1 = [minv, maxv]
    x2 = [found+2, found+2]
    plt.plot(x, valuesH, 'b')
    plt.plot(x, valuesL, 'g')
    plt.plot(x1, y1, 'r')
    plt.plot(x2, y1, 'r')
    #plt.gcf().autofmt_xdate()
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("Error : usage <ohlc_file.csv.gz>")
        quit()
    infile = sys.argv[1]
    year, month, day = 2019, 3, 8
    if len(sys.argv) > 2 :
        date = sys.argv[2]
        year, month, day = int(date[0:4]), int(date[4:6]), int(date[6:8])
    hist = ReadOHLC.read(infile)
    """
    records = sortByMax(hist)
    for i,r in enumerate(records):
        print("%s, %10.6f, %10.6f" % (r, r.H - r.L, r.O - r.C))
        if i > 20 : break
    recs = getRecords(hist, Utils.DT(2018, 2, 5, 0, 0, 0), Utils.DT(2018, 2 ,6, 0, 0,0))
    
    print(recs[0])
    print(recs[-1])
    px = [r.O for r in recs]
    x = [i for i in range(len(px))]
    plt.plot(x, px)
    plt.show()
    """
    plotRecords(hist, Utils.DT(year, month, day, 7, 25, 0), Utils.DT(year, month , day, 7, 35, 0))

if __name__ == '__main__':
    main()
