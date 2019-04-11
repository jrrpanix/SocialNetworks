import pandas as pd
import os
import datetime
import pytz

class ReadH5 :

    def __init__(self, dataDir, timeZone='US/Central', reportNoData=True):
        assert os.path.exists(dataDir)
        self.dataDir = dataDir
        self.tz = pytz.timezone(timeZone)
        self.reportNoData = reportNoData

    def findFile(self, symbol, date):
        def getdt(d,tz=self.tz) :
            #return tz.localize(datetime.datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]),0,0,0))
            return datetime.datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]),0,0,0)

        for f in os.listdir(self.dataDir):
            if not symbol in f : continue
            d0, d1 = getdt(f.split("_")[1]), getdt(f.split("_")[2])
            if date >= d0 and date <= d1: return f
        return None
            

    def readh5(self, symbol, date):
        fname = self.findFile(symbol, date)
        if fname is None:
            if self.reportNoData :
                print("no data for this symbol:date %s:%s" % (symbol, date))
            return None
        return pd.read_hdf(os.path.join(self.dataDir, fname), 'table')

        
