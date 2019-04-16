import h5py
import numpy as np
import pandas as pd
import os
import sys
import argparse
import math
from pytz import timezone

#TZ_Central = timezone("US/Central")

"""
 This code attempts to filter down the announcements
 to the basic core.
"""

class EventFilter:

    def __init__(self, infile=None, tz=timezone("US/Central")):
        self.names=["dt", "currency", "description", "impact", "actual", "forecast", "previous","event"]
        self.usecols = [0,1,2,3,4,5,6,7]
        self.tz = tz
        if infile is not None:
            self.create(infile)

    def create(self, infile):

        def clean(x):
            # convert messy numbers with units to a float
            # A bit of a hack, removes units and curriencies embeded into
            # the forecast so it can be converted to a number
            # returns 'nan' if it can sucessfully cast to a float
            if type(x) != str : return x
            bad=["%","B","M","K","T","$","A","k","b","m","EU",u"\xA3","t",",",u'\u20ac',u"\u00A5"]
            for b in bad:
                x = x.replace(b,"")
            try:
                v = float(x)
            except:
                v= float('nan')
            return v

        df = pd.read_csv(infile, 
                         usecols=self.usecols,
                         header=None, 
                         names=self.names,
                         sep=",")
        df['dt'] = pd.to_datetime(df['dt'],format="%Y-%m-%dT%H:%M:%S")
        df['dt'] = df['dt'].apply(self.getLocalTime)
        df['actual'] = df['actual'].apply(clean)
        df['forecast'] = df['forecast'].apply(clean)
        df['previous'] = df['previous'].apply(clean)
        df = df[df['currency'] == 'usd']
        self.df = df
        return df

    def topEvents(self):
        if self.df is None :return None
        uv = sorted(self.df.event.unique())
        eC={}
        for i in range(len(uv)):
            e =uv[i]
            edf = self.df[self.df["event"]==e]
            eC[e] = len(edf)
        return sorted([(k,v) for k,v in eC.items()], key=lambda x: x[1], reverse=True)
        
    def eventdf(self, event):
        if self.df is None : return None
        return self.df[self.df["event"]==event]

    def setImpactLevel(self, impact="High"):
        if self.df is None : return None
        self.df=self.df[self.df['impact']==impact]

    def getLocalTime(self, dt):
        t0 = self.tz.localize(dt)
        t1 = self.tz.fromutc(dt)
        return dt + (t1 - t0)

    def save(self, outputFile):
        self.df.to_hdf(outputFile, 'table', table=True, complevel=9, complib='zlib', mode='w')


###################################
# Local Functions for Testing
###################################



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SocialNetworks CSV to HDF5')
    parser.add_argument('-i','--input', help='specify input directory or input file')
    parser.add_argument('-o','--output', help='specify input directory or input file')
    args = parser.parse_args()
    inputFile, outputFile = args.input, args.output
    assert os.path.exists(args.input)
    events = EventFilter(infile=inputFile)
    events.save(outputFile)
    print("events save to %s" % outputFile)
