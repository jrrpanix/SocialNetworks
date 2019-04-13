import pandas as pd
import numpy as np
import datetime
import bisect
import os


class OHLC:

    def __init__(self, D, O, H, L, C, N, V, B, A, T, Forecast=None,Prev=None,Act=None):
        self.D = D # event Date Time 
        self.beginD = D - datetime.timedelta(seconds=B)
        self.endD = D + datetime.timedelta(seconds=A)
        self.O = O # open
        self.H = H # high
        self.L = L # low
        self.C = C # close
        self.N = N # N Obs in interval
        self.V = V # trade volume
        self.B = B # seconds before D
        self.A = A # seconds after D
        self.T = T # Tick Size
        self.range = H - L
        self.ticks = self.range/T
        self.R = (C - O)/O # interval return
        self.Forecast = Forecast
        self.Prev = Prev
        self.Act = Act


class ComputeOHLC :
    # written due to complexity in pandas with non-unique datetimes
    # df   - pandas dataframe , columns [dt,price,qty] dt=datetime of row
    # date - datetime of event
    # secBefore - window start
    # secAfter - window end
    # T = ticksize (NQ,ES = 0.25, UB,UB = 1/32, TU, FV, TY = 1/64)
    def calc(df, date, secBefore, secAfter, T):
        datesV = df.dt.values
        delta = datetime.timedelta(seconds=10)
        before = date - datetime.timedelta(seconds=secBefore)
        after  = date + datetime.timedelta(seconds=secAfter)
        ib, ia = bisect.bisect_left(datesV, np.datetime64(before)),bisect.bisect_right(datesV, np.datetime64(after)) 
        if ib < 0 or ib >= len(df) : return None
        if ia < 0 or ia >= len(df) : return None
        ie=ia+1
        O, C = df.iloc[ib-1]["price"], df.iloc[ia]["price"]
        V= df.iloc[ib-1:ie]["qty"].sum()
        L, H= df.iloc[ib-1:ie]["price"].min(),df.iloc[ib-1:ie]["price"].max()
        return OHLC(date, O, H, L, C, ie - ib + 1, V, secBefore, secAfter, T)
 

def Test(ddir, fname, T=1.0/32, B=900, A=900, H=7, M=30, S=0):
    df =pd.read_hdf(os.path.join(ddir, fname), 'table')
    dmin, dmax = df.dt.min(), df.dt.max()
    start = datetime.datetime(dmin.year, dmin.month, dmin.day, H, M, S)
    if start < dmin:
        start = start + datetime.timedelta(days=1)
    for i in range(500):
        if start.weekday() < 5:
            oh = ComputeOHLC.calc(df, start, B, A, T)
            if oh is not None:
                print("%s %6.0f" % (oh.D, oh.ticks))
        start = start + datetime.timedelta(days=1)
        if start > dmax : break


if __name__ == '__main__':
    ddir="~/TickData/splits/"
    fname="UB_20190314_20190404.h5"
    Test(ddir, fname)

