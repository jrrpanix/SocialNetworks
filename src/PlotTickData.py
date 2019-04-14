import sys
import os
import argparse
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np

from ReadH5 import ReadH5

def getDT(d,t):
    return datetime.datetime(int(d[0:4]), int(d[4:6]), int(d[6:8]), int(t[0:2]), int(t[2:4]), int(t[4:6]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SocialNetworks: Analyze Trump')
    parser.add_argument('--dataDir', help='specify tick data directory', default= "/Users/john/TickData/splits")
    parser.add_argument('--title', default=None)
    parser.add_argument('-s','--symbol', help='symbol ', default="ES")
    parser.add_argument('-d','--date', help='date ')
    parser.add_argument('-t','--time', help='time ')
    parser.add_argument('-w','--window', help='before window minutes ', default=120, type=int)
    args = parser.parse_args()

    dt = getDT(args.date, args.time)
    reader  = ReadH5(args.dataDir, reportNoData=False)    
    before = dt - datetime.timedelta(minutes=args.window)
    after = dt + datetime.timedelta(minutes=args.window)
    title = args.symbol + " " + dt.strftime("%m-%d-%Y")
    if args.title is not None:
        title = args.title + " " + title

    df = reader.readh5(args.symbol, dt)
    df = df[df["dt"] > before]
    df = df[df["dt"] < after]
    fig, ax = plt.subplots(figsize=(15,7))
    df.plot(x="dt",y="price",ax=ax, title=title)
    ax.plot([dt, dt], [df.price.min(), df.price.max()], 'r')
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
    plt.show()
