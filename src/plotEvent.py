import gzip
import sys
import os
import binascii
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np

class Utils:

    def DT(year, month, day, hour=0, minute=0, second=0):
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


class OHLC:

    def __init__(self, ts0, O, H, L, C, T, V, ts=None):
        self.ts0, self.O, self.H, self.L, self.C, self.T, self.V, self.ts = ts0, O, H, L, C, T, V, ts
        if self.ts is None : self.ts = self.ts0

    def __str__(self):
        return ("%s,%10.6f,%10.6f,%10.6f,%10.6f,%6d,%6d") % (str(self.ts0),self.O, self.H, self.L, self.C, self.T, int(self.V))

class ReadOHLC:

    def read(infile):
        records=[]
        with gzip.open(infile) as rdr:
            for line in rdr:
                records.append(Utils.parse(line))
        return records


class PlotEvent:

    def __init__(self, data, lowerBound, upperBound, eventTime, contract, event):
        l , u , e = PlotEvent.getIx(data, lowerBound), \
            PlotEvent.getIx(data,upperBound), \
            PlotEvent.getIx(data, eventTime)
        dates = [data[i].ts0 for i in range(l, u)]
        Ov = [data[i].O for i in range(l, u)]
        Cv = [data[i].C for i in range(l, u)]
        minO, minC = np.min(Ov), np.min(Cv)
        maxO, maxC = np.max(Ov), np.max(Cv)
        minV = np.min([minO, minC])
        maxV = np.max([maxO, maxC])

        eventInData = data[e].ts0
        eventDate = eventTime.strftime("%m/%d/%Y")
        title = "%s %s %s" % (contract, event, eventDate)
       
        fig, ax = plt.subplots()
        ax.set(title=title)
        ax.plot(dates, Ov, 'g')
        ax.plot(dates, Cv, 'b')
        ax.plot([eventInData, eventInData], [minV,maxV], 'r')
        timeFmt = DateFormatter("%H:%M:%S")        
        ax.xaxis.set_major_formatter(timeFmt)
        plt.show()

    def getIx(data, date):
        b, e = 0 , len(data)
        while True:
            m = int((b +e)/2)
            d =data[m].ts0 
            if d == date : 
                return m
            if date < d : e = m
            else: b = m
            if e - b <= 1 :
                return b
        return b

def main():
    if len(sys.argv) < 5:
        print("usage : <data file OHLC.csv.gz> <Event> <EventDate YYYYMMDD> <EventTime HH:MM>")
        quit()
    infile = sys.argv[1]
    event = sys.argv[2]
    eventDate = sys.argv[3]
    eventHour = int(sys.argv[4].split(':')[0])
    eventMinute = int(sys.argv[4].split(':')[1])
    lb = Utils.DT(int(eventDate[0:4]), int(eventDate[4:6]), int(eventDate[6:8]))
    ub = lb + datetime.timedelta(days=1)
    eventTime = Utils.DT(lb.year, lb.month, lb.day, eventHour, eventMinute)
    data = ReadOHLC.read(infile)
    contract = os.path.splitext(os.path.basename(infile))[0].split("_")[0]
    PlotEvent(data, lb, ub, eventTime, contract, event)


if __name__ == '__main__':
    # example usage
    # python ./plotEvent.py ../data/UB_OHLC_30.csv.gz  non-farm-payrolls 20190201 7:30
    main()


