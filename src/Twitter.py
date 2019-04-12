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
import bisect

class Twitter :

    def __init__(self, twitterFile, startDate=None):
        df = pd.read_csv(twitterFile, 
                         usecols=[0,1,2,3,4,5,6],
                         header=0,
                         names=None,
                         dtype=None, #{"source":"str", "text":"str", "created_at": "str", "retweet_count":"str", "favorite_count":"str", "is_retweet":"str", "id_str":"str"},
                         sep=",")
        df=df.dropna()
        df['created_at'] = pd.to_datetime(df['created_at'],format="%m-%d-%Y %H:%M:%S")    
        df=df.set_index('created_at')
        if startDate is not None:
            df=df[df.index > p]
        self.df = df
        



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SocialNetworks Analyze Event')
    parser.add_argument('-t','--twitter', help='specify tick data directory', default= "../data/trump_twitter.csv")
    args = parser.parse_args()

    twitter = Twitter(args.twitter)
    print(twitter.df)





