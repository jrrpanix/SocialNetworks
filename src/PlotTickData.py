import sys
import os
import argparse
import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import numpy as np
import bisect

from ReadH5 import ReadH5
from Utils import Utils

def GetValueBefore(df, dt, tag="price"):
    datesV=df.dt.values
    ib = bisect.bisect_left(datesV, np.datetime64(dt))
    if ib > 1 and ib < len(df):
        return df.iloc[ib-1][tag]
    return None

def PlotTickData(dt, df, symbol, window, title_prefix=None, dfmt='%H:%M:%S', units=None, before_seconds=15, contracts=100):
    before = dt - datetime.timedelta(minutes=window)
    after = dt + datetime.timedelta(minutes=window)
    title = symbol + " " + dt.strftime("%m-%d-%Y")
    if units == "dollars":
        title = title + (":$MOVE CONTRACTS=%d" % int(contracts))
    elif units == "ticks":
        title = title + ":TickMove"
    if title_prefix is not None:
        title = title_prefix + " " + title

    df = df[df["dt"] > before]
    df = df[df["dt"] < after]
    fig, ax = plt.subplots(figsize=(15,7))
    if units is not None:
        p0=GetValueBefore(df, dt - datetime.timedelta(seconds=before_seconds))
        df["dPrice"] = df["price"] - p0
        if units == "ticks":
            df["ticks"] = df["dPrice"] / Utils.tickSize(symbol)
            df.plot(x="dt",y="ticks",ax=ax, title=title)
            ax.plot([dt, dt], [df.ticks.min(), df.ticks.max()], 'r')
        elif units == "dollars":
            df["dollars"] = df["dPrice"] / Utils.tickSize(symbol) * Utils.tickValue(symbol) * contracts
            df.plot(x="dt",y="dollars",ax=ax, title=title)
            ax.plot([dt, dt], [df.dollars.min(), df.dollars.max()], 'r')
        else:
            df.plot(x="dt",y="dPrice",ax=ax, title=title)
            ax.plot([dt, dt], [df.dPrice.min(), df.dPrice.max()], 'r')
    else:
        df.plot(x="dt",y="price",ax=ax, title=title)
        ax.plot([dt, dt], [df.price.min(), df.price.max()], 'r')
    ax.xaxis.set_major_formatter(DateFormatter(dfmt))
    plt.show()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='SocialNetworks: Analyze Trump')
    parser.add_argument('--dataDir', help='specify tick data directory', default= os.path.join(os.getenv("HOME"),"TickData/splits"))
    parser.add_argument('--title', default=None)
    parser.add_argument('-s','--symbol', help='symbol ', default="ES")
    parser.add_argument('-d','--date', help='date of event yyyymmdd')
    parser.add_argument('-c','--contracts', help='number of contracts ', type=float, default=100.0)
    parser.add_argument('-t','--time', help='time of event hhmmss')
    parser.add_argument('-u','--units', help='units to measure in (default, ticks, dollars)', default=None)
    parser.add_argument('-w','--window', help='before window minutes ', default=120, type=int)
    args = parser.parse_args()

    dt = Utils.dt(args.date + " " + args.time, 3)
    reader  = ReadH5(args.dataDir, reportNoData=False)    
    df = reader.readh5(args.symbol, dt)
    PlotTickData(dt, df, args.symbol, args.window, "NFP", units=args.units, contracts=args.contracts)
