import h5py
import numpy as np
import pandas as pd
import os
import sys
import argparse
import math


class Announcement:

    def __init__(self):
        self.names=["dt", "currency", "description", "impact", "actual", "forecast", "previous"]
        self.usecols = [0,1,2,3,4,5,6]
        self.dtypes={'dt':'str','currency':'str','description':'str',
                     'impact':'str','actual':'str',
                     'forecast':'str', 'previous':'str'}

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
            #value = value.upper()
            return value

        df = pd.read_csv(infile, 
                         usecols=self.usecols,
                         header=None, 
                         names=self.names,
                         dtype=self.dtypes,
                         sep=",")
        df['dt'] = pd.to_datetime(df['dt'],format="%Y-%m-%dT%H:%M:%S")
        df['actual'] = df['actual'].apply(clean)
        df['forecast'] = df['forecast'].apply(clean)
        df['previous'] = df['previous'].apply(clean)
        df['event'] = df['description'].apply(normalize)
        df = df[df['currency'] == 'usd']
        return df

ann = Announcement()
df=ann.create(infile = "/Users/john/SocialNetworks/data/announcements-dailyfx.csv")
uv = sorted(df.event.unique())
for i in range(len(uv)):
    print(i, uv[i])
#print(df.iloc[0:10])




