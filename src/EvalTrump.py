import numpy as np
import pandas as pd
import os
import sys
import argparse
import datetime

from ReadH5 import ReadH5
from Twitter import Twitter
from OHLC import OHLC
from OHLC import ComputeOHLC
from Announcement import Announcement

def getTickSize(symbol):
    if symbol in ["ES", "NQ"] : return 0.25
    if symbol in ["US", "UB"] : return 1/32.0
    if symbol in ["FV", "TY"] : return 1/64.0
    if symbol in ["TU"] : return 1/128.0
    if symbol in ["EC"] : return 0.00005
    assert False, "Future %s not in Split Directory" % symbol


class GenerateTweetStats:

    def __init__(self,output, twitterFile, dataDir, symbol, before, after, DataStart=datetime.datetime(2015, 1, 2)):
        self.symbol = symbol
        self.before = before
        self.after = after
        self.TickSize = getTickSize(symbol)
        self.TwitterInfo = Twitter(twitterFile)
        self.h5Reader  = ReadH5(dataDir, reportNoData=False)
        self.wfd = open(args.output, "w")
        self.Tdf = self.TwitterInfo.df
        self.DataStart = DataStart
        self.NotRun = []
        self.run()
        self.wfd.close()
        Neval = len(self.Tdf) - len(self.NotRun)
        print("Complete total_tweets=%d, eval_tweets=%d, not_eval=%d" %
              (len(self.Tdf), Neval, len(self.NotRun)))

    def run(self):
        print("Starting Analysis of %d tweets using %s" % (len(self.Tdf), self.symbol))
        for i in range(len(self.Tdf)):
            tweetTime = self.Tdf.index[i]
            if tweetTime < self.DataStart or tweetTime.weekday() > 4:
                self.NotRun.append(tweetTime)
                continue
            tickdf = self.h5Reader.readh5(self.symbol, tweetTime)
            if tickdf is None:
                self.NotRun.append(tweetTime)
                continue
            self.evalTweet(tweetTime, tickdf)

    def evalTweet(self, tweetTime, tickdf):
        beforeTime = tweetTime - datetime.timedelta(seconds=after+60)
        beforeTweet = ComputeOHLC.calc(tickdf, beforeTime, self.before, self.after, self.TickSize)
        tweet = ComputeOHLC.calc(tickdf, tweetTime, self.before, self.after, self.TickSize)
        if tweet.V > 0 :
            self.writeRow(tweet, beforeTweet)
        else:
            self.NotRun.append(tweetTime)
        
    def header(self):
        header="tweet_time,tweet_end,tweet_R,tweet_T,tweet_O,tweet_C,tweet_L,tweet_H,tweet_N,tweet_V,tweet_N,before_time,before_end,before_R,before_T,before_O,before_C,before_L,before_H,before_N,before_V,tweet_N"        
        self.wfd.write("%s\n", header)
        
    def writeRow(self, tweet, beforeTweet):
        self.wfd.write("%s,%s,%f,%f,%f,%f,%f,%f,%f,%f,%s,%s,%f,%f,%f,%f,%f,%f,%f,%f\n" % \
                           (tweet.D,
                            tweet.endD,
                            tweet.R, 
                            tweet.ticks, 
                            tweet.O, 
                            tweet.C,
                            tweet.L,
                            tweet.H,
                            tweet.V,
                            tweet.N,
                            beforeTweet.D,
                            beforeTweet.endD,
                            beforeTweet.R, 
                            beforeTweet.ticks,
                            beforeTweet.O, 
                            beforeTweet.C,
                            beforeTweet.L,
                            beforeTweet.H,
                            beforeTweet.V,
                            beforeTweet.N
                            ))
        


if __name__ == "__main__":
    # Note the CME Futures Data Timestamps are in Central Time
    # Trump Twitter Times are in Eastern Time
    defaultFile="../data/trump_twitter.csv"
    defaultFile="../data/trump_tweets_2016_2019.csv"
    parser = argparse.ArgumentParser(description='SocialNetworks: Analyze Trump')
    parser.add_argument('-t','--twitterFile', help='twitter csv file', default=defaultFile)
    parser.add_argument('-d','--dataDir', help='specify tick data directory', default= "/Users/john/TickData/splits")
    parser.add_argument('-s','--symbol', help='symbol ', default="ES")
    parser.add_argument('-b','--before', help='before window seconds ', default=60, type=int)
    parser.add_argument('-a','--after', help='after window seconds', default=600*3, type=int)
    parser.add_argument('-o','--output', help='output file')
    args = parser.parse_args()

    twitterFile, dataDir, symbol, before, after, output = args.twitterFile, args.dataDir, args.symbol, args.before, args.after, args.output
    assert os.path.exists(twitterFile) 
    assert os.path.exists(dataDir)
    
    GenerateTweetStats(output, twitterFile, dataDir, symbol, before, after)
