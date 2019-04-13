import h5py
import numpy as np
import pandas as pd
import os
import sys
import argparse
import math
import datetime
import time
import bisect
from pytz import timezone

class Twitter :

    def __init__(self, twitterFile, startDate=None, tz=timezone("US/Central")):
        self.tz=tz
        df = pd.read_csv(twitterFile, 
                         usecols=[0,1,2,3,4,5,6],
                         header=0,
                         names=None,
                         dtype=None, #{"source":"str", "text":"str", "created_at": "str", "retweet_count":"str", "favorite_count":"str", "is_retweet":"str", "id_str":"str"},
                         sep=",")
        df=df.dropna()
        df['created_at'] = pd.to_datetime(df['created_at'],format="%m-%d-%Y %H:%M:%S")    
        df['created_at'] = df['created_at'].apply(self.getLocalTime)
        df=df.set_index('created_at')
        
        if startDate is not None:
            df=df[df.index > p]
        self.df = df
        
    def getLocalTime(self, dt):
        t0 = self.tz.localize(dt)
        t1 = self.tz.fromutc(dt)
        return dt + (t1 - t0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SocialNetworks Analyze Event')
#    parser.add_argument('-t','--twitter', help='specify tick data directory', default= "../data/trump_twitter.csv")
#    parser.add_argument('-t','--twitter', help='specify tick data directory', default= "../data/tweets2.csv")
    parser.add_argument('-t','--twitter', help='specify tick data directory', default= "./sample.csv")
    args = parser.parse_args()

    twitter = Twitter(args.twitter)
    print(twitter.df)





