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


class AnalyzeEvent:

    def __init__(self, tickDir, announcementFile, event, symbol, showLoadTimes=True):
        self.showLoadTimes=showLoadTimes
        self.event = event
        self.symbol = symbol
        assert os.path.exists(tickDir)
        assert os.path.exists(announcementFile)
        self.tickReader = ReadH5(tickDir)
        self.announcements = pd.read_hdf(announcementFile, 'table')
        if len(self.announcements) == 0:
            print("No announcements found in file %s" % announcementFile)
            assert len(self.announcements) > 0
        self.tickdf = None
        self.eventTimes = self.announcements[self.announcements["event"] == self.event]
        if len(self.eventTimes) == 0:
            print("No Event Times Found For Event %s" % event)
            assert len(self.eventTimes) > 0

    def run(self):
        for i in range(len(self.eventTimes)):
            date = self.eventTimes.iloc[i]["dt"]
            data = self.getTickData(date)
            if self.tickdf is not None:
                print("Found data for %s %d" % (date, len(self.tickdf)))

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
    args = parser.parse_args()

    tickDir, announcementFile, event, symbol = args.tickDir, args.announcementFile, args.event, args.symbol
    assert os.path.exists(tickDir)
    assert os.path.exists(announcementFile)
    

    analyze = AnalyzeEvent(tickDir, announcementFile, event, symbol)
    analyze.run()





