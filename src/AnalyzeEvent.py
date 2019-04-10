import h5py
import numpy as np
import pandas as pd
import os
import sys
import argparse
import math
import pytz
import datetime

from Announcement import Announcement
from ReadH5 import ReadH5

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='SocialNetworks Analyze Event')
    parser.add_argument('--tickdir', help='specify tick data directory', default= "/Users/john/TickData/splits")
    parser.add_argument('--anndir', help='announcement directory', default="../data/announcements-dailyfx.csv")
    parser.add_argument('--event', help='event name', default="changeinnonfarmpayrolls")
    parser.add_argument('--symbol', help='symbol ', default="ES")
    args = parser.parse_args()
    assert os.path.exists(args.tickdir)
    assert os.path.exists(args.anndir)
    

    reader = ReadH5(args.tickdir)
    ann = Announcement(args.anndir)
    print("ann done")
    ann.setImpactLevel("High")
    eventTimes = ann.eventdf(args.event)
    symbol = args.symbol

    df=None
    for i in range(len(eventTimes)):
        date = eventTimes.iloc[i]["dt"]
        print(date)
        if df is not None and date < df["dt"].max():
            print("ok")
            continue
        df = reader.readh5(symbol, date)
        if df is not None:
            print("found", date, len(df))


    #topEvents = ann.topEvents()
    #nfp = topEvents[2][0]
    #print(nfp)



