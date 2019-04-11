import h5py
import numpy as np
import pandas as pd
import os
import sys
import argparse
import math
import pytz
import datetime
import time

from ReadH5 import ReadH5

class EventStats :

    def __init__(self, zone, eData):
        self.date = eData["dt"]
        self.begin, self.end = zone.iloc[0]["dt"], zone.iloc[-1]["dt"]
        self.p0, self.p1 = zone.iloc[0]["price"], zone.iloc[-1]["price"]
        self.trades = len(zone)
        self.volume = zone["qty"].sum()
        self.maxP , self.minP = zone["price"].max(), zone["price"].min()
        self.forecast, self.actual, self.previous = eData["forecast"], eData["actual"], eData["previous"]
        

class AnalyzeEvent:

    def __init__(self, tickDir, announcementFile, event, symbol, window, showLoadTimes=True, reportNoData=True):
        self.showLoadTimes=showLoadTimes
        self.event = event
        self.symbol = symbol
        assert os.path.exists(tickDir)
        assert os.path.exists(announcementFile)
        self.tickReader = ReadH5(tickDir, reportNoData=reportNoData)
        self.announcements = pd.read_hdf(announcementFile, 'table')
        self.window = window
        if len(self.announcements) == 0:
            print("No announcements found in file %s" % announcementFile)
            assert len(self.announcements) > 0
        self.tickdf = None
        self.stats = []
        self.eventTimes = self.announcements[self.announcements["event"] == self.event]
        if self.showLoadTimes: print(self.eventTimes.columns)
        if len(self.eventTimes) == 0:
            print("No Event Times Found For Event %s" % event)
            assert len(self.eventTimes) > 0

    def run(self):
        for i in range(len(self.eventTimes)):
            eventData = self.eventTimes.iloc[i]
            date= eventData["dt"]
            data = self.getTickData(date)
            if self.tickdf is not None:
                estats = self.getStats(data, date, eventData, self.window)
                if estats is not None:
                    self.stats.append(estats)

    def getStats(self, data, date, eventData, Minutes, Seconds=0):
        t0 = time.time()
        dT = datetime.timedelta(seconds=Seconds, minutes=Minutes)
        before, after = date - dT , date + dT
        zone = data[data["dt"] > before]
        zone = zone[zone["dt"] < after]
        if len(zone) == 0 : return None
        return EventStats(zone, eventData)

    def getTickData(self, date):
        if self.tickdf is not None and date < self.tickdf["dt"].max():
            return self.tickdf
        else:
            t0 = time.time()
            self.tickdf = self.tickReader.readh5(self.symbol, date)
            t1 = time.time()
            if self.showLoadTimes and self.tickdf is not None:
                print("TickData for date %s loaded in %f (sec)" % (date, (t1 - t0)))
            return self.tickdf


    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SocialNetworks Analyze Event')
    parser.add_argument('-t','--tickDir', help='specify tick data directory', default= "/Users/john/TickData/splits")
    parser.add_argument('-a','--announcementFile', help='announcement hdf5 file', default="../data/dailyfx.h5")
    parser.add_argument('-e','--event', help='event name', default="changeinnonfarmpayrolls")
    parser.add_argument('-s','--symbol', help='symbol ', default="ES")
    parser.add_argument('-w','--window', help='window', default=30, type=int)
    args = parser.parse_args()

    tickDir, announcementFile, event, symbol, window = args.tickDir, args.announcementFile, args.event, args.symbol, args.window
    assert os.path.exists(tickDir)
    assert os.path.exists(announcementFile)
    
    startTime = time.time()
    analyze = AnalyzeEvent(tickDir, announcementFile, event, symbol, window, showLoadTimes=False, reportNoData=False)
    analyze.run()
    endTime = time.time()
    startDate, endDate, N, totalTime = None, None, len(analyze.stats), (endTime - startTime)
    if len(analyze.stats) > 0 :
        startDate, endDate = analyze.stats[0].date, analyze.stats[-1].date

    print("%s\n%s\nDates=%d\n%s-%s\nExecution Time %f (sec)" % (symbol, event, N, startDate.strftime("%m/%d/%Y"), 
                                                                endDate.strftime("%m/%d/%Y"), totalTime))
    stats = analyze.stats
    for s in stats:
        print("%s %s %s %6.1f %6.1f %6.1f %9.3f %9.3f %8.3f %8.3f %6d %7.0f" % 
              (s.date.strftime("%m/%d/%Y %H:%M:%S"), s.begin.strftime("%H:%M:%S"), s.end.strftime("%H:%M:%S"),
               s.actual, s.forecast, (s.actual - s.forecast),
               s.p0, s.p1, (s.p1 - s.p0), (s.maxP - s.minP), s.trades, s.volume))
                               
                               
                  




