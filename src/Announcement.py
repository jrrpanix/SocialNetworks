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

class Announcement:

    def __init__(self, infile=None, tz=timezone("US/Central")):
        self.names=["dt", "currency", "description", "impact", "actual", "forecast", "previous"]
        self.usecols = [0,1,2,3,4,5,6]
        self.dtypes={'dt':'str','currency':'str','description':'str',
                     'impact':'str','actual':'str',
                     'forecast':'str', 'previous':'str'}
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

        def normalize(x):
            # normalize the announcemnet
            # 
            #
            sv = x.split(" ")
            value = ""
            for word in sv:
                if word == "USD" : continue
                if "(" in word : continue
                if ")" in word : continue
                value += word
            if "Fed" in value :
                fed=["Speak", "Conference", "Discuss", "Panel", "Remark", "Speech", 
                     "Address", "Press", "speak", "Holds", "Give", "Meet", "speech", "Deliver", "Takes",
                     "Participates", "Moderat", "discuss", "Testif"]
                for f in fed:
                    if f in value:
                        value = "FedOfficialSpeaking"
                        break
            if "U.S.toSell" in value or "U.S.Sells" in value or "U.S.to" in value or "UStoSell" in value:
                value = "TreasuryAuction"
            if "Trump" in value:
                value = "TrumpRemark"
            fedo=["Yellen", "Powell", "Bernanke"]
            for f in fedo:
                if f in value:
                    value="FedChairComments"
                    break
            value=value.replace("-","")
            value=value.replace(".","")
            value = value.lower()
            return value

        df = pd.read_csv(infile, 
                         usecols=self.usecols,
                         header=None, 
                         names=self.names,
                         dtype=self.dtypes,
                         sep=",")
        df['dt'] = pd.to_datetime(df['dt'],format="%Y-%m-%dT%H:%M:%S")
        #
        # Note this is horrible and slow but its the only way
        # i could figure out how to convert the times to the
        # central time zone without carrying the timezone aware stuff
        df['dt'] = df['dt'].apply(self.getLocalTime)

        df['actual'] = df['actual'].apply(clean)
        df['forecast'] = df['forecast'].apply(clean)
        df['previous'] = df['previous'].apply(clean)
        df['event'] = df['description'].apply(normalize)
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
    parser.add_argument('-i','--input', help='specify input directory or input file', default="../data/announcements-dailyfx.csv")
    parser.add_argument('-o','--output', help='specify input directory or input file')
    parser.add_argument('-5','--h5', help='hdf5 input file to validate that output file created makes sense', default=None)
    args = parser.parse_args()
    inputFile, outputFile, h5File = args.input, args.output, args.h5
    if h5File is not None:
        df=pd.read_hdf(h5File, 'table')
        nfp=df[df["event"]=="changeinnonfarmpayrolls"]
        low=df[df["impact"]=="Low"]
        high=df[df["impact"]=="High"]
        print(len(nfp), len(low), len(high))
    else:
        assert os.path.exists(args.input)
        print("getting data from %s" % inputFile)
        announcementData = Announcement(infile=inputFile)
        announcementData.save(outputFile)
        print("saved filed %s" % outputFile)

