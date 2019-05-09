import pandas as pd
import os
import datetime
import pytz
import time
import numpy as np
from Utils import Utils

class ReadH5 :

    def __init__(self, dataDir, timeZone='US/Central', reportNoData=True):
        assert os.path.exists(dataDir)
        self.dataDir = dataDir
        self.tz = pytz.timezone(timeZone)
        self.reportNoData = reportNoData
        self.df = None
        self.symbol = None

    def findFile(self, symbol, date):
        for f in os.listdir(self.dataDir):
            base, ext = os.path.splitext(f)
            if not symbol in base or len(base.split("_")) < 3: continue
            d0, d1 = Utils.dt(base.split("_")[1]), Utils.dt(base.split("_")[2])
            date = Utils.todt(date)
            if date >= d0 and date <= d1: return f
        return None
            

    def readh5(self, symbol, date):
        if self.df is not None:
            date = Utils.todt(date)
            if self.symbol == symbol:
                if date > self.start_date and date < self.end_date :
                    return self.df
        fname = self.findFile(symbol, date)
        if fname is None:
            self.df = None
            if self.reportNoData :
                print("no data for this symbol:date %s:%s" % (symbol, date))
            return None
        t0 = time.time()
        self.df =pd.read_hdf(os.path.join(self.dataDir, fname), 'table')
        self.start_date, self.end_date = self.df['dt'].min(), self.df['dt'].max()
        self.symbol= symbol
        t1 = time.time()
        if self.reportNoData :
            print("reading time for %s %f" % (fname, (t1-t0)))
        return self.df
        

    def setIndex(self):
        # Not used for now
        self.df.set_index('dt', inplace=True)
